+ [BB-162](http://tickets.musicbrainz.org/browse/BB-162)

```python
def list_get_single(self):
line: rand_limit = random.randint(0,len(instances)+3)
change to: rand_limit = random.randint(-1,len(instances)+3)
```

+ [BB-163](http://tickets.musicbrainz.org/browse/BB-163)
```python
def bad_delete_tests(self):
line: # self.bad_delete_double_tests()
change to: self.bad_delete_double_tests()
```

+ [BB-164](http://tickets.musicbrainz.org/browse/BB-164)

+ [BB-165](http://tickets.musicbrainz.org/browse/BB-165)

+ [BB-166](http://tickets.musicbrainz.org/browse/BB-166)


+ [BB-167](http://tickets.musicbrainz.org/browse/BB-167)
```python
def bad_bbid_general_get_tests(self, instances):
# gid_bad = change_one_character(str(entity_gid))
# self.bbid_one_get_test(None, gid_bad, correct_result=False)
# see ws_bugs.md
```

+ [BB-168](http://tickets.musicbrainz.org/browse/BB-168)
+ [BB-169](http://tickets.musicbrainz.org/browse/BB-169)
