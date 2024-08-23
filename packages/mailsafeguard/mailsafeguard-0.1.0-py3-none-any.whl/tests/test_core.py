# tests/test_core.py
import sys
import os
import unittest

# Add the path to the mailsafeguard package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mailsafeguard')))

# Import the function to test
from core import is_disposable_email

class TestMailSafeGuard(unittest.TestCase):

    def setUp(self):
        # Set up any necessary test data or state
        self.test_emails = [
           'test@gmail.com',         
        'user@outlook.com',        
        'example@yahoo.com',       
        'person@thowfick.com', 
        'contact@mailinator.com',  
        'admin@amazon.com',
        'admin@in.ew.sd.re.we.ds.qw.as.xz.cx.vc.bv.gf.tr.tu.fg.amazon.com',
        'admin@in.ew.sd.re.we.ds.qw.as.xz.cx.vc.bv.gf.google.com' 
        ]
    
    def test_disposable_emails(self):
        for email in self.test_emails:
            with self.subTest(email=email):
                result = is_disposable_email(email)
                print(f'Email: {email} | Is Disposable: {result}')
                

if __name__ == '__main__':
    unittest.main()
