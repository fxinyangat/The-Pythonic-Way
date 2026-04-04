from account import Account

class FlexipayAccount(Account):
    def createAccount(self):
        info = self.account_details
        print(info)
        print(f"Created Flexipy Account:\n Owner: {info[0]['owner']}\nAcc Numbner: {info[1]['acc_number']}")
        
  
class SavingsAccount(Account):
    def createAccount(self):
        info = self.account_details
        print(info)
        print(f"Created Savings Account:\n Owner: {info[0]['owner']}\nAcc Numbner: {info[1]['acc_number']}")
        
        
    def withdraw_funds(self, amount:float):
        #allow withdraw up to 50% of balance.
        balance = self.check_balance
        try:
            self._validate_amount(amount,'withdraw')
        except Exception as e:
            print(f"Failed to withdraw from savings accoun: {e}")
        else:   
            allowed_amt = balance*0.5
            if amount > allowed_amt:
                print('50 percent error')
                raise ValueError('Can not withdraw more than 50 percent of balance.')
            self._balance -= amount
            
            return f"Withdraw succefull - New Balacne: {self.check_balance}"


class CheckingAccount(Account):
    def createAccount(self):
        info = self.account_details
        print(info)
        print(f"Created checking Account:\n Owner: {info[0]['owner']}\nAcc Numbner: {info[1]['acc_number']}")
        
    
    def withdraw_funds(self, amount:float):
        #allow withdraw up to 50% of balance extra.
        balance = self.check_balance
        overdraft_amount = balance + (balance*0.5)
        try:
            if amount > overdraft_amount:
                print('50 percent overdraft error')
                raise ValueError(f'Can not withdraw more than allowed  ${overdraft_amount} overdraft')
            
        except Exception as e:
            print(f"Failed to withdraw from checking accoun: {e}")
        else:   
            
            self._balance -= amount
            
            return f"Withdraw succefull - New Balacne: {self.check_balance}"
        
        
    
if __name__ == "__main__":
    flexi = FlexipayAccount(owner="Sid Jain")
    # flexi.createAccount()
    # flexi.account_details
    # print(flexi.deposit_funds(100))
    # print(flexi.withdraw_funds(10))
    
    sacco = SavingsAccount(owner="Sam Ninsiima")
    sacco.createAccount()
    # sacco.account_details
    # sacco.check_balance
    # sacco.deposit_funds(1000)
    # print(sacco.withdraw_funds(200))
    # print(sacco.deposit_funds(2000))
    
    midfirst = CheckingAccount(owner="Florence Ofori")
    midfirst.createAccount()
    midfirst.account_details
    sacco.check_balance
    midfirst.deposit_funds(100)
    
    print(midfirst.withdraw_funds(155))
    # print(midfirst.deposit_funds(20))
    print(midfirst.account_status)
    print(midfirst.close_account())
    

    
    
    
    