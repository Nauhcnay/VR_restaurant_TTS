import os
import sys
# old_file_name = "/home/career_karma/raw_data.csv"
# new_file_name = "/home/career_karma/old_data.csv"

# os.rename(old_file_name, new_file_name)
#if __name__ == "__main__":
    
folder =sys.argv[1]
path  = "C:\\Users\\z5308\\Desktop\\Workplace_VR_projects\\workplaceVR\\Input\\VR_restaurant_TTS\\CustAudioSetting\\"+ "{0}\\".format(folder)
#os.getcwd()
for file in os.listdir(path):
    print(file)
    # if(file.endswith("s00.wav")):
    #       os.remove(path+file)
    if(file.startswith("g")):
        s =  file.replace("g", "",1)
        s = s.strip('0123456789')
        print(s)
        os.rename(path+file, path+s)
    
print("File renamed for {0}".format(path))