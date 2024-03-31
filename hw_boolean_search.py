#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import codecs
from csv import writer
#! to fix: 

#



#! optimization 

# 2) вместо одного большого словаря можно создать массив словарей


class Index:
    def __init__(self):
        self._inv_index = dict()
    
    #! all words are added to index in lowercase 
    def fill_index(self,index_filepath):
        with codecs.open(index_filepath,mode="r",encoding="utf-8") as ind_file:
            for line in ind_file:
                words = line.rstrip("\n").split()
                doc_num = int(words[0][1:])
                for i in range(1,len(words)):

                    # transforming word to correct format
                    cur_word = words[i].strip().lower()
                    if (words[i].strip().lower()) in self._inv_index:
                        self._inv_index[cur_word].add(doc_num)
                    else:
                        self._inv_index.update({cur_word:set([doc_num])})

    #! all terms must be searched in lowercase format
    def fetch_docset(self,term):
        term_lower = term.lower()
        if term_lower in self._inv_index:
            return self._inv_index[term_lower]
        else:
            return set()

    def print_index(self):
        for key,value in self._inv_index.items():
            print(key,value)    



class Expr_obj:
    operations = ["(",")"," ","|"]


    #! retrieve data by directly accessing fields
    def __init__(self,obj_string):
        self.is_op = obj_string in self.operations
        self.op_type = self._get_op_type(obj_string)
        self.op_index = self._get_op_index(obj_string)
        self.obj_value = None 
        self.obj_string = obj_string


    def __str__(self):
        return "is_op: {}, op_type: {}, op_index: {}, obj_value: {}, obj_string: {}".format(self.is_op, self.op_type,
                                                                               self.op_index,self.obj_value,self.obj_string)
    
    def _get_op_type(self,obj_string):
        if self.is_op:
            return obj_string
        else:
            return None 

    def _get_op_index(self,obj_string):
        if self.is_op:
            return self.operations.index(obj_string)
        else:
            return None
    
    def set_obj_value(self,doc_set):
        self.obj_value = doc_set



# uses Shunting yard algorithm under hood
# evaluates expressions - returns set of documents that are relevant to the query 
class Evaluator:
    def __init__(self,index):
        self._cur_result = {}
        self._index = index 
        

    # first function to be called when processing query 
    def get_relevant_docs(self,query):

        token_arr = self._tokenize(query)

        poliz_arr = self._gen_poliz(token_arr)

        result = self._evaluate(poliz_arr)
        

        # list of documents that are relevant to query 
        return result.obj_value  

    # splits query into tokens and returns array of tokens (objects of Expr_obj)
    def _tokenize(self,query):

        token_arr = [] 

        def add_word(char_arr,token_arr,is_op=False):

            token_str = "".join(char_arr)
            token = Expr_obj(token_str)

            if not is_op:
                rel_docs = self._index.fetch_docset(token_str)
                token.set_obj_value(rel_docs)

            token_arr.append(token)

        cur_word = []

        for sym in query:
            if sym=="|" or sym=="(" or sym==")" or sym==" ":

                if len(cur_word)>0:
                    add_word(cur_word,token_arr,is_op=False)
                    cur_word.clear() 

                add_word([sym],token_arr,is_op=True)

            else:
                cur_word.append(sym)
        
        if len(cur_word)>0:
            add_word(cur_word,token_arr,is_op=False)
        

        return token_arr

    # converts array of tokens to poliz notation 
    def _gen_poliz(self,token_arr):
        poliz = [] 
        op_stack = [] 

        # Shunting yard algorithm

        for token in token_arr:
            if token.is_op == False:
                poliz.append(token)
            else:
                # if token found
                if token.op_type=="(":
                    op_stack.append(token)

                elif token.op_type==(")"):
                    while True:
                        popped_token = op_stack.pop()
                        if popped_token.op_type == "(":
                            break
                        else:
                            poliz.append(popped_token)
                else:
                    # op_stack can be empty 
                    while len(op_stack)>0:
                        popped_token = op_stack.pop()

                        # removing ops from op_stack until "(" or op with lower precedence foudn
                        if (popped_token.op_type == "(") or (popped_token.op_index>token.op_index):
                            op_stack.append(popped_token)
                            break
                        else:
                            poliz.append(popped_token)

                    op_stack.append(token)

        while len(op_stack)>0:
            poliz.append(op_stack.pop())

        return poliz            

                    
    # evaluates poliz notation 
    def _evaluate(self,poliz):


        def print_stack(stack):
            for elem in stack:
                print(elem)
            
            print("-----------------------------------")

        stack = [] 

        for elem in poliz:
            if elem.is_op == False:
                stack.append(elem)
            else:
            
                op1 = stack.pop()
                op2 = stack.pop()
            

                res_op = Expr_obj(obj_string=op1.obj_string+op2.obj_string)
                # string concatenation can be removed, it is ineffective and redundant


                if elem.op_type == "|":
                    #logical or
                    expr_value = op1.obj_value.union(op2.obj_value)
                else:
                    # logical and 
                    expr_value = op1.obj_value.intersection(op2.obj_value)
                    
                
                res_op.set_obj_value(expr_value)
                stack.append(res_op)

        return stack[0]
    

    # resets class fields
    def reset(self):
        self._cur_result = set()



class SearchResults:

    def __init__(self,evaluator):
        # element with ith index stores search results of ith query 
        self._query_evaluator = evaluator 
        self._query_base = [""] # all queries strings are stored in this array 
        self._csv_fields = ["ObjectId","Relevance"]

   
    def fill_query_base(self,query_file):
        with codecs.open(query_file, mode='r', encoding='utf-8') as queries_fh:
            for line in queries_fh:
                fields = line.rstrip().split('\t')
                qid = int(fields[0])
                query = fields[1]
                self._query_base.append(query)


    # returns 1 if query with query_id is relevant to doc with doc_num, otherwise returns 0 
    def _is_relevant(self,query_id,doc_num):
        
        rel_docs = self._query_evaluator.get_relevant_docs(self._query_base[query_id])
        if doc_num in rel_docs:
            return 1
        else:
            return 0 
                

    def print_submission(self, objects_filepath, submission_filepath):
        with codecs.open(objects_filepath, mode='r', encoding='utf-8') as obj_file:
            with open(submission_filepath, mode= "w",encoding="utf-8",newline="",) as csv_file:
            
                csv_writer = writer(csv_file,delimiter=",",lineterminator="\n")
                
                # writing header of csv file 
                csv_writer.writerow(self._csv_fields)

                # reading header of objects.enumerate.txt
                obj_file.readline()

                while True:
                    question_line = obj_file.readline().rstrip().split(",")

                    if question_line == [""]:
                        break
                    
                    
                    obj_id = int(question_line[0])
                    query_id = int(question_line[1])
                    doc_num = int(question_line[2][1:])
                

                    ans = self._is_relevant(query_id,doc_num)           
                    csv_writer.writerow([obj_id,ans])



def main():
    # Command line arguments.
    parser = argparse.ArgumentParser(description='Homework: Boolean Search')
    parser.add_argument('--queries_file', required = True, help='queries.numerate.txt')
    parser.add_argument('--objects_file', required = True, help='objects.numerate.txt')
    parser.add_argument('--docs_file', required = True, help='docs.tsv')
    parser.add_argument('--submission_file', required = True, help='output file with relevances')
    args = parser.parse_args()

    # Build index.
    index = Index()
    index.fill_index(args.docs_file)


    evaluator = Evaluator(index)


    # Process queries.  
    search_results = SearchResults(evaluator)
    search_results.fill_query_base(args.queries_file)

    # Generate submission file.
    search_results.print_submission(args.objects_file, args.submission_file)


if __name__ == "__main__":
    main()

