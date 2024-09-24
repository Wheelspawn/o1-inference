import random

block_num = 6
stack_num = 2

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

stacks = [[] for i in range(stack_num)]
stacks_desc = []

random.shuffle(names)

for i in range(block_num):
    stack_pos = random.randint(0,stack_num-1)
    stacks[stack_pos].append(names[i])
    if len(stacks[stack_pos]) == 1:
        stacks_desc.append("Block '{}' is stacked on top of the table.".format(stacks[stack_pos][0]))
    else:
        stacks_desc.append("Block '{}' is stacked on top of block '{}'.".format(stacks[stack_pos][-1], stacks[stack_pos][-2]))

stacks_desc.append("Block 'Lima' is red.")
stacks_desc.append("Block 'Yankee' is rectangular.")
stacks_desc.append("Block 'Zulu' weighs 140 grams.")

random.shuffle(stacks_desc)

