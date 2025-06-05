import json
import glob

# Test JSON loading
files = glob.glob('*.json')
print(f'Found JSON files: {files}')

for file in files:
    print(f'\nTesting {file}:')
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        print(f'  Loaded successfully')
        print(f'  Type: {type(data)}')
        if isinstance(data, list):
            print(f'  Items: {len(data)}')
            if len(data) > 0 and 'people' in data[0]:
                people = len(data[0]['people'])
                print(f'  People: {people}')
                if people > 0:
                    person = data[0]['people'][0]
                    pose_kp = len(person.get('pose_keypoints_2d', []))
                    print(f'  Pose keypoints: {pose_kp}')
        else:
            print('  Single object')
    except Exception as e:
        print(f'  Error: {e}')
