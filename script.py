import random

import os
from openai import OpenAI
import re

def main():
    block_num = 3 # random.randint(4,8)
    stack_num = 1 # random.randint(1,3)
    question_num = 2
    iterations = 1
    
    run_tests = False
    
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    
    names = ["Alfa",
             "November",
             "Bravo",
             "Oscar",
             "Charlie",
             "Papa",
             "Delta",
             "Quebec",
             "Echo",
             "Romeo",
             "Foxtrot",	 
             "Sierra",
             "Golf",
             "Tango",
             "Hotel",
             "Uniform",
             "India",
             "Victor",
             "Juliett",
             "Whiskey",
             "Kilo",
             "Xray",
             "Lima",
             "Yankee",
             "Mike",
             "Zulu"]
    
    letters_to_names = {n[0]:n for n in names}
    
    for i in range(iterations):
        
        stacks = [[] for i in range(stack_num)]
        stacks_desc = []
        questions = []
        theorems = []
        
        random.shuffle(names)
        
        for i in range(block_num):
            stack_pos = random.randint(0,stack_num-1)
            stacks[stack_pos].append(names[i])
            if len(stacks[stack_pos]) == 1:
                stacks_desc.append("Block '{}' is stacked on top of the table.\n".format(stacks[stack_pos][0]))
            else:
                stacks_desc.append("Block '{}' is stacked on top of block '{}'.\n".format(stacks[stack_pos][-1], stacks[stack_pos][-2]))
            
            # add a useless proposition to challenge the model's distractability
            if random.random() > 0.8:
                stacks_desc.append("Block '{}' is {}.\n".format(random.choice(names),
                                                                random.choice(["red",
                                                                               "blue",
                                                                               "green",
                                                                               "yellow",
                                                                               "white",
                                                                               "black",
                                                                               "brown",
                                                                               "orange",
                                                                               "purple",
                                                                               "gray",
                                                                               "rectangular",
                                                                               "cylindrical",
                                                                               "cubic",
                                                                               str(random.randint(100,1000))+" grams"])))
            
        random.shuffle(stacks_desc)
        
        stacks_1d = [e for s in stacks for e in s] + ['table']
        
        for i in range(question_num):
            b1,b2=random.sample(range(0, len(stacks_1d)), 2)
            if  stacks_1d[b1] == 'table':
                questions.append("Is block '{}' stacked on top of the table?\n".format(stacks_1d[b2]))
                theorems.append("{}t".format(stacks_1d[b2][0]))
            elif stacks_1d[b2] == 'table':
                questions.append("Is block '{}' stacked on top of the table?\n".format(stacks_1d[b1]))
                theorems.append("{}t".format(stacks_1d[b1][0]))
            else:
                questions.append("Is block '{}' stacked on top of block '{}'?\n".format(stacks_1d[b1],stacks_1d[b2]))
                theorems.append("{}{}".format(stacks_1d[b1][0],stacks_1d[b2][0]))
        
        
        prompt = """
Instructions:
You will be provided with a block world scenario and asked questions about the scenario. For each question, you will first output each inference step. You will do this by outputting each inference in the format XY^YZ->XZ (or XY->~YX to imply negation) where X, Y and Z are the uppercase first letter of each block name.  To refer to the table, use the lowercase letter 't'. Then output the word 'true' or 'false' (without the apostrophes), which is your answer to the question. Finally, output a newline after each question. Each inference step must be valid or the solution will not be counted as a success, even if your answer is correct. The inference rules will be given, and these will show you how to derive the correct answer.

Here is an example:

Inference rules:
If block X is stacked on top of block Y and block Y is stacked on top of block Z, then block X is above block Z (XY^YZ->XZ).
If block X is stacked on top of block Y, block Y cannot be stacked on top of block X (XY->~YX).
If block X is stacked on top of the table and block Y is stacked on top of the table, block X cannot be above block Y and block Y cannot be above block X (Xt^Yt->~XY^~YX).

Base propositions:
Block 'Sierra' is stacked on top of block 'Foxtrot'.
Block 'Foxtrot' is stacked on top of the table.
Block 'Whiskey' is stacked on top of block 'Sierra'.
Block 'Xray' is stacked on top of block 'Whiskey'.

Example questions:
Is block 'Xray' stacked on top of block 'Foxtrot'?
Is block 'Sierra' stacked on top of block 'Whiskey'?

An example of your response:
XW^WS->XS
XS^SF->XF
true

SW->~WS
false

Now here is your task:

Inference rules:
If block X is stacked on top of block Y and block Y is stacked on top of block Z, then block X is above block Z (XY^YZ->XZ).
If block X is stacked on top of block Y, block Y cannot be stacked on top of block X (XY->~YX).
If block X is stacked on top of the table and block Y is stacked on top of the table, block X cannot be above block Y and block Y cannot be above block X (Xt^Yt->~XY^~YX).

Base propositions:
{}
Questions:
{}""".format(''.join(stacks_desc), ''.join(questions))
        
        stacks_letters_only = [['t'] + [e[0] for e in s] for s in stacks]
        
        print(prompt)
        print()
        print(stacks_letters_only)
        print(questions)
        print(theorems)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4",
        )
        
        responses = chat_completion.choices[0].message.content.split("\n\n")
        
        for i in range(len(responses)):
            props = responses[i].split("\n")
            tvalues = check_proof(theorems[i],props[:-1],stacks_letters_only)
            print()
            print("{}. ChatGPT inferences: ".format(i), props)
            print("{}. Evaluated the inferences: ".format(i), tvalues)
    
    
    # all tests should print True
    if run_tests:
        print(True in check_proof("MG", ["MG"], [ ['t', 'G', 'M'] ]))
        print(False in check_proof("GM", ["GM"], [ ['t', 'G', 'M'] ]))
        print(True in check_proof("BE", ["BC^CD->BD","BD^DE->BE"], [ ['t', 'F', 'E', 'D','C','B','A'], ['t', 'Q', 'R'] ]))
        print(True in check_proof("Bt", ["BC^CD->BD","BD^DE->BE","BE^EF->BF","BF^Ft->Bt"], [ ['t', 'F', 'E', 'D','C','B','A'], ['t', 'Q', 'R'] ]))
        print(False in check_proof("EA", ["AB^BC->AC", "AC^CD->AD", "AD^DE->AE", "AE->~EA"], [ ['t', 'F', 'E', 'D','C','B','A'], ['t', 'Q', 'R'] ]))
        print(True in check_proof("~EA", ["AB^BC->AC", "AC^CD->AD", "AD^DE->AE", "AE->~EA"], [ ['t', 'F', 'E', 'D','C','B','A'], ['t', 'Q', 'R'] ]))
        print(False in check_proof("QA", ["AF^Ft->At", "At^Qt->~QA^~AQ"], [ ['t', 'F','A'], ['t', 'Q', 'R'] ]))
        print(False in check_proof("AQ", ["AF^Ft->At", "At^Qt->~QA^~AQ"], [ ['t', 'F','A'], ['t', 'Q', 'R'] ]))
        print(False in check_proof("QA^AQ", ["AF^Ft->At", "At^Qt->~QA^~AQ"], [ ['t', 'F','A'], ['t', 'Q', 'R'] ]))
        print(True in check_proof("~QA", ["AF^Ft->At", "At^Qt->~QA^~AQ"], [ ['t', 'F','A'], ['t', 'Q', 'R'] ]))
        print(True in check_proof("~AQ", ["AF^Ft->At", "At^Qt->~QA^~AQ"], [ ['t', 'F','A'], ['t', 'Q', 'R'] ]))
        print(True in check_proof("~QA^~AQ", ["AF^Ft->At", "At^Qt->~QA^~AQ"], [ ['t', 'F','A'], ['t', 'Q', 'R'] ]))
        print(True in check_proof("~QR", ["RQ->~QR"], [ ['t'], ['t', 'Q', 'R'] ]))
        print(False in check_proof("~QR", [""], [ ['t'], ['t', 'Q', 'R'] ]))
        print(False in check_proof("~QR", ["Z"], [ ['t'], ['t', 'Q', 'R'] ]))
        print(False in check_proof("~QR", ["^Q>QQ-Q^~Q>R-RRQ"], [ ['t'], ['t', 'Q', 'R'] ]))
        print(False in check_proof("RQ", ["RRRRQQQ"], [ ['t'], ['t', 'Q', 'R'] ]))
        print(False in check_proof("Rt", ["RRRRQQQ"], [ ['t'], ['t', 'Q', 'R'] ]))
        print(False in check_proof("Rt", ["RQ"], [ ['t'], ['t', 'Q', 'R', 'S'] ]))
        print(False in check_proof("Rt", ["SR^RQ->SQ", "SQ->St"], [ ['t'], ['t', 'Q', 'R', 'S'] ]))


def stacks_index(e,stacks):
    for i in range(len(stacks)):
        if e in stacks[i]:
            return (i,stacks[i].index(e))
    raise ValueError("'{}' is not in list".format(e))

def on_top_of(a,b,stacks):
    try:
        a_index = stacks_index(a,stacks)
        b_index = stacks_index(b,stacks)
        
        if a == 't':
            return False
        
        if a_index[1] == 1 and b == 't':
            return True
        
        if ((a_index[0] == b_index[0]) and (a_index[1] - b_index[1] == 1)):
            return True
        return False
    except ValueError:
        return False
    

def check_proof(theorem,props,stacks):
    
    # XY^YZ->XZ
    # ([A-Zt]{2})\^([A-Zt]{2})\->([A-Zt]{2})$
    # XY->~YX
    # ([A-Zt]{2})\->~([A-Zt]{2}$)
    # Xt^Yt->~XY^~YX
    # ([A-Zt]{1})t\^([A-Zt]{1})t\->~([A-Zt]{2})\^~([A-Zt]{2})$
    
    stacks_copy = stacks.copy()
    
    tvalues = []
    
    # print()
    # print(theorem)
    # print(props)
    # print(stacks)
    
    try:
        # pop everything above X onto the stack
        i,_ = stacks_index(props[0][0], stacks_copy)
        while (stacks_copy[i][-1] != props[0][0]):
            stacks_copy[i].pop()
    except ValueError:
        pass
    except IndexError:
        return [False]
    
    for p in props:
        
        try:
        
            if (len(p.split("->")) > 1):
                lh, rh = p.split("->")
            else:
                lh, rh = (p,p)
        
            # XY^YZ->XZ
            if (re.match("([A-Zt]{2})\^([A-Zt]{2})\->([A-Zt]{2})$", p)):
                lh_a, lh_b = lh.split("^")
                rh_a, rh_b = rh[0:2]
                
                if (on_top_of(lh_a[0],lh_a[1],stacks_copy) and
                    (lh_a[1] == lh_b[0]) and
                    on_top_of(lh_b[0],lh_b[1],stacks_copy)):
                    top = stacks_copy[i].pop()
                    stacks_copy[i].pop()
                    stacks_copy[i].append(top)
                    tvalues.append(True)
                else:
                    tvalues.append(False)
            # XY->~YX
            elif (re.match("([A-Zt]{2})->~([A-Zt]{2}$)", p)):
                
                if ((lh[0] == rh[2]) and (lh[1] == rh[1])):
                    if (on_top_of(lh[0],lh[1],stacks_copy)):
                        tvalues.append(True)
                    else:
                        tvalues.append(False)
                else:
                    tvalues.append(False)
            # Xt^Yt->~XY^~YX
            elif (re.match("([A-Zt]{1})t\^([A-Zt]{1})t->~([A-Zt]{2})\^~([A-Zt]{2})$", p)):
                lh_xt, lh_yt = lh.split("^")
                rh_xy, rh_yx = rh.split("^")
                
                # Xt^Yt->~XY^~YX
                if (on_top_of(lh_xt[0],'t',stacks_copy) and
                    on_top_of(lh_yt[0],'t',stacks_copy) and
                    (lh_xt[0] == rh_xy[1]) and 
                    (lh_yt[0] == rh_xy[2]) and
                    (lh_xt[0] == rh_yx[2]) and
                    (lh_yt[0] == rh_yx[1])):
                    tvalues.append(True)
                # Xt^Yt->~YX^~XY (logically equivalent but we have to check it anyways)
                elif (on_top_of(lh_xt[0],'t',stacks_copy) and
                      on_top_of(lh_yt[0],'t',stacks_copy) and
                      (lh_xt[0] == rh_xy[2]) and 
                      (lh_yt[0] == rh_xy[1]) and
                      (lh_xt[0] == rh_yx[1]) and
                      (lh_yt[0] == rh_yx[2])):
                    tvalues.append(True)
                else:
                    tvalues.append(False)
                
            # XY
            elif (re.match("([A-Zt]{2})", p)):
                lh_a, lh_b = p
                if (on_top_of(lh_a,lh_b,stacks_copy) and lh_a+lh_b == theorem):
                    tvalues.append(True)
                else:
                    tvalues.append(False)
            else:
                tvalues.append(False)
            
        except ValueError:
            tvalues.append(False)
            
    # if A -> B -> ... -> N and N then the proof is complete, return True
    if (False not in tvalues) and (rh == theorem or theorem in rh.split("^")):
        tvalues.append(True)
    # if A -> B is false but B -> C -> ... -> N is true then ~(A->N)
    else:
        tvalues.append(False)
        
    return tvalues
            
if __name__ == "__main__":
    main()


