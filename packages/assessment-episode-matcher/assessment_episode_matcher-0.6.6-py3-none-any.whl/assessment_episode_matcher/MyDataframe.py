import pandas as pd

# # assessment_episode_matcher/mytypes.py
# class Descriptor:
#   def __init__(self, base_fields: dict[str, str]):
#     self.fields = base_fields


# class MyDataFrame(pd.DataFrame):
#   _metadata = ['descriptors']

#   def __init__(self, descriptors, **kwargs):
#       super().__init__( **kwargs)
#       self._descriptors = descriptors

#   @property
#   def descriptors(self) -> Descriptor | None:
#     return self._descriptors

#   @descriptors.setter
#   def descriptors(self, value: Descriptor):
#     self._descriptors = value

#_metadata:
# if you want to ensure that the my_descriptor attribute is copied along when the DataFrame is copied or created, 
# you would need to use _metadata. Here's how you can do it:

if __name__ == '__main__':

  # dcr = Descriptor({"program": "MURUMPP"})
  df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
  # df = MyDataFrame( {"A": [1, 2], "B": [3, 4]} , descriptors=dcr)
  df.attrs['programs']= ['MURUMPP', 'ATOM']

  
  print(df)