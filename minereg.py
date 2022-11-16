# This module Controls mining

"""
Things like Multi miner bonus
and,
mining for a long time bonus(name pending lol)
"""

def LMTB(jsonloco,user): # Long Mining Time Bonus also known as LMTB
    if jsonloco < 60: #0
        Bonus_reward = 0
    else:
        if jsonloco < 120:
            Bonus_reward = 0.00009
            #print("60sec bonus applied! to "+user)
        else:
            if jsonloco < 180:
                Bonus_reward = 0.0005
                #print("120sec bonus applied! to "+user)
            else:
                Bonus_reward = 0.0007
                #print("180 bonus applied! to "+user)
         
    return int(Bonus_reward)

def MultiMine(jsonuser):
    # TODO: work on multiminer bonus
    pass 
    