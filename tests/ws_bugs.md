+ **When making a get request on /entity_name/ and passing limit = -1,
there is an exception from SQL raised and not HTML 400 code returned**
[BB-162](http://tickets.musicbrainz.org/browse/BB-162)

```python
function: def list_get_single(self):
line: rand_limit = random.randint(0,len(instances)+3)
change to: rand_limit = random.randint(-1,len(instances)+3)
```

+ **When making a delete request on /entity_name/bbid twice,
there is an exception raised and not HTML 400 code returned**
```python
def bad_delete_tests(self):
line: # self.bad_delete_double_tests()
change to: self.bad_delete_double_tests()
```

+ **Bad type requests are triggering exceptions, but 400 HTTP code should be returned.**
**function:** 

lines to uncomment:
```python
function: def post_tests(self):
# for i in range(BAD_POST_TESTS_COUNT):
#   self.put_post_bad_tests('post')  
```

+ **Bad type requests are triggering exceptions, but 400 HTTP code should be returned (similar as in POST earlier)**

lines to uncomment:
```python
function: def put_tests(self):
#for i in range(BAD_PUT_TESTS_COUNT):   
#   self.put_post_bad_tests('put')  
```  


+ **When passing null as a value to some attribute in put, it doesn't change to null (if it wasn't already null).**
**lines to delete**:
```python
function: def equality_simply_objects_check(self, ws_object, db_object):
if ws_object == None:  
    return  
```

+ **Querying /ws/entity/{some_valid_bbid}/relationships/
works only with the trailing slash, unlike all other requests**

+ **Sometimes get/:id with bad id raises an SQL exception and doesn't return a 404 signal
(I've seen it when 'L' was added at the end of valid id)**
lines to uncomment:
```python
function: def bad_bbid_general_get_tests(self, instances):
# gid_bad = change_one_character(str(entity_gid))
# self.bbid_one_get_test(None, gid_bad, correct_result=False)
# see ws_bugs.md
```
