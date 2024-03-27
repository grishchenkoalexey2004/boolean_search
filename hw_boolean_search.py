#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import codecs
import sys

#! to fix: 

#



#! optimization 

# 2) вместо одного большого словаря можно создать массив словарей


class Index:
    def __init__(self, index_filepath):
        self._inv_index = dict()
        self._fill_index(index_filepath)
    
    def _fill_index(self,index_filepath):
        with open(index_filepath) as ind_file:
            for line in ind_file:
                words = line.rstrip("\n").split()
                doc_num = int(words[0][1:])
                for i in range(1,len(words)):
                    if (words[i].strip()) in self._inv_index:
                        self._inv_index[words[i].strip()].add(doc_num)
                    else:
                        self._inv_index.update({(words[i]).strip():set([doc_num])})

    def fetch_docset(self,term):
        if term in self._inv_index:
            return self._inv_index[term]
        else:
            return dict()

    def print_index(self):
        for key,value in self._inv_index.items():
            print(key,value)    



class Expr_obj:
    operations = ["(",")"," ","|"]


    #! retrieve data by directly accessing fields
    def __init__(self,obj_string,index):
        self.is_op = obj_string in self.operations
        self.op_type = self._get_op_type(obj_string)
        self.op_index = self._get_op_index(obj_string)
        self.obj_value = self._get_obj_value(obj_string,index)
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
    
    def _get_obj_value(self,obj_string,index):
        if self.is_op == False:
            return index.fetch_docset(obj_string)
        else:
            return None




# uses Shunting yard algorithm under hood
# evaluates expressions - returns set of documents that are relevant to the query 
class Evaluator:
    def __init__(self,index):
        self._cur_result = {}
        self._index = index 

    # first function to be called when processing query 
    def get_relevant_docs(self,query):


        token_arr = self._tokenize(query)

        for elem in token_arr:
            print(elem)

        print("-----------------------------------------------------------")

        poliz_arr = self._gen_poliz(token_arr)

        for elem in poliz_arr:
            print(elem)

        return None  

    # splits query into tokens and returns array of tokens in same order 
    def _tokenize(self,query):

        token_arr = [] 

        def add_word(char_arr,token_arr):

            token_str = "".join(char_arr)
            token = Expr_obj(token_str,self._index)
            token_arr.append(token)

        cur_word = []

        for sym in query:
            if sym=="|" or sym=="(" or sym==")" or sym==" ":

                if len(cur_word)>0:
                    add_word(cur_word,token_arr)
                    cur_word.clear() 

                add_word([sym],token_arr)

            else:
                cur_word.append(sym)
        
        if len(cur_word)>0:
            add_word(cur_word,token_arr)
        

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
    def _evaluate(self,query):
        pass  

    # resets class fields
    def reset(self):
        self._cur_result = dict()



class SearchResults:
    def add(self, found):
        # TODO: add next query's results
        pass

    def print_submission(self, objects_file, submission_file):
        # TODO: generate submission file
        pass


def main():
    # Command line arguments.
    parser = argparse.ArgumentParser(description='Homework: Boolean Search')
    parser.add_argument('--queries_file', required = True, help='queries.numerate.txt')
    parser.add_argument('--objects_file', required = True, help='objects.numerate.txt')
    parser.add_argument('--docs_file', required = True, help='docs.tsv')
    parser.add_argument('--submission_file', required = True, help='output file with relevances')
    args = parser.parse_args()

    # Build index.
    index = Index(args.docs_file)
    evaluator = Evaluator(index)


    # Process queries.  
    search_results = SearchResults()
    with codecs.open(args.queries_file, mode='r', encoding='utf-8') as queries_fh:
        for line in queries_fh:
            fields = line.rstrip('\n').split('\t')
            qid = int(fields[0])
            query = fields[1]

            # process query 
            evaluator.reset()
            query_result  = evaluator.get_relevant_docs(query)
            
            # search_results.add(query_result)

    # Generate submission file.
    search_results.print_submission(args.objects_file, args.submission_file)
    #index.print_index()

if __name__ == "__main__":
    main()

