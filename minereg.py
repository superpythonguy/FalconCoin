# This module Controls mining

"""
Things like Multi miner bonus
and,
mining for a long time bonus(name pending lol)
"""

import random, os, time

Randrop_amount = 1.5 # FLC

def LMTB(jsonloco,user): # Long Mining Time Bonus also known as LMTB
    if jsonloco < 0: #0
        Bonus_reward = 0
    else:
        if jsonloco < 3600: # 1 hour of mining bonus
            Bonus_reward = 0.00009
            #print("1h bonus applied! to "+user)
            
        else:
            if jsonloco < 10800: # 3 hour of mining bonus
                Bonus_reward = 0.0005
                #print("3h bonus applied! to "+user)
                
            else:
                if jsonloco < 21600:# 6 hours of mining
                    Bonus_reward = 0.006
                    #print("6h bonus applied! to "+user)
                    
                else:
                    if jsonloco < 43200:#12 hour bonus
                        Bonus_reward = 0.09
                        
                    else:# 12+ bonus
                        Bonus_reward = 0.29
         
    return int(Bonus_reward)


