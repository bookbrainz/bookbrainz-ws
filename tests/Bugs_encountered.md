+ When making a get request on /entity_name/ and passing limit = -1,  
there is an exception from SQL raised and not HTML 400 code returned   
**function:** 
```def list_get_single(self)```  
**line**: ```rand_limit = random.randint(0,len(instances)+3)```  
**change to**: ```rand_limit = random.randint(-1,len(instances)+3)```


+ When making a delete request on /entity_name/bbid twice,  
there is an exception raised and not HTML 400 code returned   
**function:** 
```def bad_delete_tests(self)```  
**line**: ```# self.bad_delete_double_tests()```  
**change to**: ```self.bad_delete_double_tests()```  


+ Bad type requests are triggering exceptions, but 400 HTTP code should be returned.  
**function:** 
```def post_tests(self)```  
**line**: ``` #self.put_post_bad_tests('post') ```  
**change to**: ``` self.put_post_bad_tests('post') ```  


+ Bad type requests are triggering exceptions, but 400 HTTP code should be returned (similiar as in POST earlier)  
**function:** 
```def put_tests(self)```  
**line**: ``` #self.put_post_bad_tests('put') ```  
**change to**: ``` self.put_post_bad_tests('put') ```  



