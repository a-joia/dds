
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import api.client as client

path1 = 'acciatartaruswestus.westus/PlatformUPAWest/SecondVeryNiceTable/Field3/SubField1'
path2 = 'acciatartaruswestus.westus/PlatformUPAWest/AnvilBugCheckSubscriptionID/Field1'

print('Checking if fields exist:')
print('Field 1:', client.get_field_by_path('acciatartaruswestus.westus', 'PlatformUPAWest', 'SecondVeryNiceTable', 'Field3', 'SubField1'))
print('Field 2:', client.get_field_by_path('acciatartaruswestus.westus', 'PlatformUPAWest', 'AnvilBugCheckSubscriptionID', 'Field1'))

print(f'Adding equivalence between {path1} and {path2}')
add_result = client.add_equivalence(path1, path2)
print('Add equivalence result:', add_result)

print('Equivalents for', path1, ':', client.list_equivalents(path1))
print('Equivalents for', path2, ':', client.list_equivalents(path2))

print(f'Removing equivalence between {path1} and {path2}')
# remove_result = client.remove_equivalence(path1, path2)
# print('Remove equivalence result:', remove_result) 