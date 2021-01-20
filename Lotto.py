from tkinter import Widget

AWARD_X = "10,000,000"
AWARD_S = "2,000,000"
AWARD_H = "200,000"
AWARD_2 = "40,000"
AWARD_3 = "10,000"
AWARD_4 = "4,000"
AWARD_5 = "1,000"
AWARD_6 = "200"
AWARD_E = "200"

class Lotto:
    def __init__(self):
        self.period = "00000"           
        self.award_X = "00000000"   # 特別獎
        self.award_S = "00000000"   # 特獎
        self.award_H = []           # 頭獎
        self.award_E = []           # 增開六獎
    def __init__(self,per,X,S,H,E):
        self.period = per
        self.award_X = X
        self.award_S = S
        self.award_H = H
        self.award_E = E
    def __str__(self):
        msg = "統一發票" + self.period + "期\n"
        msg += "特別獎: " + self.award_X + '\n'
        msg += "    特獎: " + self.award_S + '\n'
        msg += "    頭獎: "
        flag = 0
        for ah in self.award_H:
            if(flag==0):
                msg += ah + "\n"
            else:
                msg += "              " +ah+ '\n'
            flag+=1
        msg += "    六獎: "
        for ex in self.award_E:
            msg += ex + " "
        msg += "\n-----------------------------"
        return msg
    def redeem(self, target = "xxxxxxxx"):
        # 特別獎\特獎\頭獎
        if(target == self.award_X):         
            return target + " 特別獎 " + AWARD_X
        
        if(target == self.award_S):         
            return target + " 特獎 " + AWARD_S
        
        for h in self.award_H:              
            if(target == h):
                return target + " 頭獎 " + AWARD_H
        # 頭獎以下   
        rtarget = "".join(reversed(target))     # reverse invoice code
        max_match = 0
        for hcode in self.award_H:
            match = 0
            rhcode = "".join(reversed(hcode))
            for i in range(0, len(rhcode)):
                if(rtarget[i] == rhcode[i]):
                    match += 1
                else:
                    break
            if(match > max_match):
                max_match = match

        if(max_match >= 7):
            return target + " 二獎 " + AWARD_2
        elif(max_match >=6):
            return target + " 三獎 " + AWARD_3
        elif(max_match >=5):
            return target + " 四獎 " + AWARD_4
        elif(max_match >=4):
            return target + " 五獎 " + AWARD_5
        elif(max_match >=3):
            return target + " 六獎 " + AWARD_6    
        
        for ex in self.award_E:
            if(ex == target[-3:]):
                return target + " 六獎 " + AWARD_E
        return target + " 摃龜"




