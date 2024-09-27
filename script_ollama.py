import csv
from openai import OpenAI
import os
import random
import re

def main():
    models = ["gpt-4", "gpt-4-turbo", "gpt-4o"]
    block_num = 3 # random.randint(4,8)
    block_num_max = 8
    stack_num = 2 # random.randint(1,3)
    question_num = 3
    iterations = 0
    run = 0
    run_len = 30
    
    current_model = "gpt-4o"
    
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
    
    with open('results.csv', 'w', newline='') as csvfile:
        output_writer = csv.writer(csvfile, delimiter=';',
                                   quotechar='|', quoting=csv.QUOTE_MINIMAL)
        output_writer.writerow(["Iteration",
                                "Run",
                                "Model",
                                "Number of blocks",
                                "Number of stacks",
                                "Number of base propositions",
                                "Number of useless propositions",
                                "Number of questions/response pairs in this iteration",
                                "Current question/response pair",
                                "Base propositions",
                                "Question",
                                "Model proposed inferences",
                                "Model proposed conclusion",
                                "Correct inferences",
                                "Number of inferences true",
                                "Number of inferences false",
                                "Sound argument?"])
        
        while (block_num < block_num_max):
            for i in range(run_len):
                
                stacks = [[] for i in range(stack_num)]
                base_props = []
                useless_props = 0
                questions = []
                theorems = []
                
                random.shuffle(names)
                
                for b in range(block_num):
                    stack_pos = random.randint(0,stack_num-1)
                    stacks[stack_pos].append(names[b])
                    if len(stacks[stack_pos]) == 1:
                        base_props.append("Block '{}' is stacked on top of the table.\n".format(stacks[stack_pos][0]))
                    else:
                        base_props.append("Block '{}' is above block '{}'.\n".format(stacks[stack_pos][-1], stacks[stack_pos][-2]))
                    
                    # add a useless proposition to challenge the model's distractability
                    if random.random() > 0.90:
                        base_props.append("Block '{}' is {}.\n".format(random.choice(names),
                                                                       random.choice([str(random.randint(10,1000))+" grams",
                                                                                      str(random.randint(10,1000))+" millimeters wide",
                                                                                      str(random.randint(10,1000))+" centimeters tall",
                                                                                      str(random.randint(10,1000))+" cubic centimeters"])))
                        useless_props += 1
                    
                random.shuffle(base_props)
                
                stacks_1d = [e for s in stacks for e in s] + ['table']
                
                for q in range(question_num):
                    b1,b2=random.sample(range(0, len(stacks_1d)), 2)
                    if  stacks_1d[b1] == 'table':
                        questions.append("Is block '{}' stacked on top of the table?\n".format(stacks_1d[b2]))
                        theorems.append("{}t".format(stacks_1d[b2][0]))
                    elif stacks_1d[b2] == 'table':
                        questions.append("Is block '{}' stacked on top of the table?\n".format(stacks_1d[b1]))
                        theorems.append("{}t".format(stacks_1d[b1][0]))
                    else:
                        questions.append("Is block '{}' above block '{}'?\n".format(stacks_1d[b1],stacks_1d[b2]))
                        theorems.append("{}{}".format(stacks_1d[b1][0],stacks_1d[b2][0]))
                        
                prompt = """
Instructions:
You will be provided with a block world scenario and asked questions about the scenario. For each question, you need to deduce the answer, output each inference step you've taken, and display the answer. You will do this by outputting each inference in valid symbolic logic (XY, AB^BC->AC, SF->~FS, etc.). Then output the word 'true' or 'false' (without the apostrophes), which is your conclusion. Finally, output a semicolon on a newline to signal completion of the answer. You must write the example exactly in that format. Do not add any other text, commentary or formatting, or your solution will be considered invalid.

Each inference step must be valid or the solution will not be counted as a success, even if your final answer is correct. The inference rules will be given, and these will show you how to derive the correct answer. If you cannot derive an answer from the given inference rules, you can assume the question is false and may simply output 'false'. If the answer is trivial (i.e. the answer is given by a base proposition) then simply output that base proposition along with 'true'.

Inference rules:
If block X is above block Y, then XY.
If block X is placed on the table, then Xt (note that all blocks are above the table, but only some blocks touch the table).
If block X is above block Y and block Y is above block Z, then block X is above block Z (XY^YZ->XZ).
If block X is above block Y, block Y cannot be above block X (XY->~YX).

Base propositions (example):
Block 'Sierra' is above block 'Foxtrot'.
Block 'Foxtrot' is placed on the table.
Block 'Whiskey' is above block 'Sierra'.
Block 'Xray' is above block 'Whiskey'.
Block 'Hotel' is placed on the table.

Qestions (example):
Is block 'Xray' above block 'Foxtrot'?
Is block 'Sierra' above block 'Whiskey'?
Is block 'Sierra' above block 'Hotel'?

Your responses (example):
XW^WS->XS
XS^SF->XF
true
;
SW->~WS
false
;
false
;

Base propositions:
{}
Questions:
{}
Your responses:
    """.format(''.join(base_props), ''.join(questions))
            
                stacks_letters_only = [['t'] + [e[0] for e in s] for s in stacks]
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=current_model,
                )
                
                print(chat_completion.choices[0].message.content)
                responses = chat_completion.choices[0].message.content.split(";")[:-1]
                print("Responses: ", responses)
                
                for r in range(len(responses)):
                    model_proposals = responses[r].strip("\n").split("\n")
                    if len(model_proposals) == 1:
                        model_proposals = [""] + model_proposals;
                    print("Proposals: ", model_proposals)
                    print()
                    tvalues = check_proof(theorems[r],model_proposals[:-1],stacks_letters_only)
                    # print()
                    # print("{}. Model inferences: ".format(r), model_proposals)
                    # print("{}. Evaluated inferences: ".format(r), tvalues)
                    
                    output_writer.writerow([iterations,
                                            run,
                                            current_model,
                                            block_num,
                                            stack_num,
                                            len(base_props),
                                            useless_props,
                                            question_num,
                                            r,
                                            ''.join([b.strip("\n") + " " for b in base_props]),
                                            questions[r].strip("\n"),
                                            ''.join([str(proposal) + ", " for proposal in model_proposals[:-1]]),
                                            model_proposals[-1],
                                            ''.join([str(v) + ", " for v in tvalues]),
                                            len([p for p in tvalues if p==True]),
                                            len([p for p in tvalues if p==False]),
                                            'false' if False in tvalues else 'true'])
                    iterations += 1
            run += 1
            block_num += 1
                
# all tests should print True
def run_tests():
    tests = [
        [True, check_proof("MG", ["MG"], [ ['t', 'G', 'M'] ])],
        [False, check_proof("GM", ["GM"], [ ['t', 'G', 'M'] ])],
        [True, check_proof("BE", ["BC^CD->BD","BD^DE->BE"], [ ['t', 'F', 'E', 'D','C','B','A'], ['t', 'Q', 'R'] ])],
        [True, check_proof("Bt", ["BC^CD->BD","BD^DE->BE","BE^EF->BF","BF^Ft->Bt"], [ ['t', 'F', 'E', 'D','C','B','A'], ['t', 'Q', 'R'] ])],
        [False, check_proof("EA", ["AB^BC->AC", "AC^CD->AD", "AD^DE->AE", "AE->~EA"], [ ['t', 'F', 'E', 'D','C','B','A'], ['t', 'Q', 'R'] ])],
        [True, check_proof("~EA", ["AB^BC->AC", "AC^CD->AD", "AD^DE->AE", "AE->~EA"], [ ['t', 'F', 'E', 'D','C','B','A'], ['t', 'Q', 'R'] ])],
        [False, check_proof("QA", ["AF^Ft->At", "At^Qt->~QA^~AQ"], [ ['t', 'F','A'], ['t', 'Q', 'R'] ])],
        [False, check_proof("AQ", ["AF^Ft->At", "At^Qt->~QA^~AQ"], [ ['t', 'F','A'], ['t', 'Q', 'R'] ])],
        [False, check_proof("QA^AQ", ["AF^Ft->At", "At^Qt->~QA^~AQ"], [ ['t', 'F','A'], ['t', 'Q', 'R'] ])],
        [True, check_proof("~QA", ["AF^Ft->At", "At^Qt->~QA^~AQ"], [ ['t', 'F','A'], ['t', 'Q', 'R'] ])],
        [True, check_proof("~AQ", ["AF^Ft->At", "At^Qt->~QA^~AQ"], [ ['t', 'F','A'], ['t', 'Q', 'R'] ])],
        [True, check_proof("~QA^~AQ", ["AF^Ft->At", "At^Qt->~QA^~AQ"], [ ['t', 'F','A'], ['t', 'Q', 'R'] ])],
        [True, check_proof("~QR", ["RQ->~QR"], [ ['t'], ['t', 'Q', 'R'] ])],
        [True, check_proof("~QR", ["RQ->~QR"], [ ['t'], ['t', 'Q', 'R'] ])],
        [False, check_proof("~QR", ["Z"], [ ['t'], ['t', 'Q', 'R'] ])],
        [False, check_proof("~QR", ["^Q>QQ-Q^~Q>R-RRQ"], [ ['t'], ['t', 'Q', 'R'] ])],
        [False, check_proof("RQ", ["RRRRQQQ"], [ ['t'], ['t', 'Q', 'R'] ])],
        [False, check_proof("Rt", ["RRRRQQQ"], [ ['t'], ['t', 'Q', 'R'] ])],
        [False, check_proof("Rt", ["RQ"], [ ['t'], ['t', 'Q', 'R', 'S'] ])],
        [False, check_proof("Rt", ["SR^RQ->SQ", "SQ->St"], [ ['t'], ['t', 'Q', 'R', 'S'] ])],
        [True, check_proof("DF", [""], [ ['t','A'], ['t','B','C','D'], ['t','E','F'] ])],
        [False, check_proof("Bt", [""], [ ['t','A'], ['t','B','C','D'], ['t','E','F'] ])],
        [False, check_proof("Ct", [""], [ ['t','A'], ['t','B','C','D'], ['t','E','F'] ])],
        [False, check_proof("Et", [""], [ ['t','A'], ['t','B','C','D'], ['t','E','F'] ])],
        [False, check_proof("DB", [""], [ ['t','A'], ['t','B','C','D'], ['t','E','F'] ])],
        [False, check_proof("tC", [""], [ ['t','A'], ['t','B','C','D'], ['t','E','F'] ])] ]
    
    for i in range(len(tests)):
        print("{}. {}".format(i, tests[i][0] == (False if False in tests[i][1] else True)))

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
        
        if ((a_index[0] == b_index[0]) and (a_index[1] - b_index[1] == 1) and (a != b)):
            return True
        return False
    except ValueError:
        return False

def above(a,b,stacks):
    try:
        a_index = stacks_index(a,stacks)
        b_index = stacks_index(b,stacks)
        
        if a == 't':
            return False
        
        if b == 't':
            return True
        
        if ((a_index[0] == b_index[0]) and (a_index[1] - b_index[1] > 0) and (a != b)):
            return True
        return False
    except ValueError:
        return False

def check_proof(props,stacks):
    
    # list of regex search patterns
    therefore = "([A-Za-z\s]+).( Therefore )([A-Za-z\s]+)"
    connectives = "( and | or )"
    is_above = "( and )|( is above )"
    not_above = "([A-Za-z]+)( is not above )([A-Za-z\s]+)"
    placed_on_table = "([A-Za-z]+)( is placed on the table)"
    diff_stack = "([A-Za-z]+)( is on a different stack than )([A-Za-z\s]+)"
    
    # will be true for every true inference and False for every false inference
    tvals = []
    
    for p in props:
        
        try:
            # If ... therefore ... .
            r = re.findall(therefore, p)[0]
            
            if r:
                
                ant = r[0] # antecedent
                con = r[2] # consequent
                
                ant_tval = True
                con_tval = True
                
                # what pattern does the antecedent follow?
                # connectives: ' and ' or ' or '
                
                op=re.split(connectives, ant)
                print(op)
                
                if (op_split:=re.split(" and | is above ", ant)):
                    print("1: ", op_split)
                    for i in range(0,len(op_split),2):
                        # check if X is above Y
                        x = op_split[i]
                        y = op_split[i+1]
                        
                        if above(x,y,stacks) == False:
                            ant_tval = False
                            break
                        
                    # check if consequent matches antecedent and X is above Z
                    con_split = re.split("and | is above ", ant)
                    con_tval = (op_split[0] == con_split[0]) and (op_split[-1] == con_split[-1])
                    
                elif (op_split:=re.findall(not_above, op)):
                    print("2: ", op_split)
                    ant_tval = above(op_split[0],op_split[2])
                    
                elif (op_split:=re.findall(placed_on_table, op)):
                    print("3: ", op_split)
                    ant_tval = on_top_of(op_split[0],'t')
                    
                elif (op_split:=re.findall(diff_stack, op)):
                    print("4: ", op_split)
                    
                    b1,b2=op_split[0],op_split[2]
                    b1_stack = stacks_index(b1,stacks)[0]
                    b2_stack = stacks_index(b2,stacks)[0]
                    
                    ant_tval = (b1_stack == b2_stack)
                else:
                    ant_tval = False
                
                print("ant_tval: ", ant_tval)
                print("con_tval: ", con_tval)
                tvals.append(ant_tval and con_tval)
            else:
                # string not in proper If ... therefore ... . syntax
                tvals.append(False)
        except Exception as err:
            # something unknown went wrong
            print(err)
            tvals.append(False)
            
    return tvals

a = check_proof(["Foxtrot is above Sierra and Sierra is above Hotel. Therefore Foxtrot is above Hotel."],[['t','Hotel','Sierra','Foxtrot'],['t']])
b = check_proof(["Foxtrot is above Sierra and Sierra is above Hotel. Therefore Hotel is not above Foxtrot."],[['t','Hotel','Sierra','Foxtrot'],['t']])
c = check_proof(["Alfa is placed on the table and Foxtrot is placed on the table. Therefore Alfa is on a different stack than Foxtrot."],[['t','Alfa','Foxtrot'],['t','Golf']])

'''
if __name__ == "__main__":
    main()
'''
