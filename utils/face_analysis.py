import pandas as pd
import boto3
import io
from PIL import Image
import math

credential = pd.read_csv("new_user_credentials.csv")
access_key_id = credential['Access key ID'][0]
secret_access_key = credential['Secret access key'][0]

client = boto3.client('rekognition', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)


def get_analysis(img):
    result={}
    statement=""
    try:

        # photo1 = cv2.imread(img)
        # imgHeight, imgWidth, channels = photo1.shape
        source_img = Image.open("static/uploads/"+img)
        bytes_array = io.BytesIO()
        source_img.save(bytes_array, format="PNG")
        request = {
            'Bytes': bytes_array.getvalue()
        }

        response=client.detect_faces(Image=request, Attributes=['ALL'])

        if response['FaceDetails'] != []:
            for index,details in enumerate(response['FaceDetails']):
                result[index]={}
                #face bounding box details
                face = details['BoundingBox']

                #cropping process
                img_width, img_height = source_img.size
                width = img_width * face['Width']
                height = img_height * face['Height']
                left = img_width * face['Left']
                top = img_height * face['Top']
                area = (left, top, left + width, top + height)
                cropped_image = source_img.crop(area)

                # saving cropped images
                path="result"+str(index)+".png"
                cropped_image.save("static/result/"+path, "PNG")

                # emotion detail extraction
                conf = 0
                emotion = ""
                for lst in details['Emotions']:
                    if conf < lst['Confidence']:
                        conf = lst['Confidence']
                        emotion = lst['Type']
                conf=math.floor(conf * 10 ** 2) / 10 ** 2

                # checking for eyeglasses
                eye_glass=""
                if details['Eyeglasses']['Value'] == True:
                    eye_glass="wearing"
                elif details['Eyeglasses']['Value'] == False:
                    eye_glass="not wearing"

                # checking for sunglasses
                sun_glass = ""
                if details['Sunglasses']['Value'] == True:
                    sun_glass = "wearing"
                elif details['Sunglasses']['Value'] == False:
                    sun_glass = "not wearing"

                # checking for eyes open or not
                eye_open = ""
                if details['EyesOpen']['Value'] == True:
                    eye_open = "Open"
                elif details['EyesOpen']['Value'] == False:
                    eye_open = "Closed"

                # checking for mouth is open or not
                mouth_open = ""
                if details['MouthOpen']['Value'] == True:
                    mouth_open = "Open"
                elif details['MouthOpen']['Value'] == False:
                    mouth_open = "Closed"

                # checking for Beard or not
                beard = ""
                if details['Beard']['Value'] == True:
                    beard = "has"
                elif details['Beard']['Value'] == False:
                    beard = "does not have"


                # creating new dictionary to show in UI
                print(details['Confidence'])
                result[index]['face_confidence']= math.floor(details['Confidence'] * 10 ** 2) / 10 ** 2
                result[index]['face_path']=path
                result[index]['gender']={}
                result[index]['gender']['value']=details['Gender']['Value']
                result[index]['gender']['confidence'] = math.floor(details['Gender']['Confidence'] * 10 ** 2) / 10 ** 2
                result[index]['age_range']=str(details['AgeRange']['Low'])+" - "+str(details['AgeRange']['High'])
                result[index]['emotion'] = {}
                result[index]['emotion']['value'] = emotion
                result[index]['emotion']['confidence'] =conf
                result[index]['eye_glass'] = {}
                result[index]['eye_glass']['value'] = eye_glass
                result[index]['eye_glass']['confidence'] = math.floor(details['Eyeglasses']['Confidence'] * 10 ** 2) / 10 ** 2
                result[index]['sun_glass'] = {}
                result[index]['sun_glass']['value'] = sun_glass
                result[index]['sun_glass']['confidence'] = math.floor(details['Sunglasses']['Confidence'] * 10 ** 2) / 10 ** 2
                result[index]['eye_open'] = {}
                result[index]['eye_open']['value'] = eye_open
                result[index]['eye_open']['confidence'] = math.floor(details['EyesOpen']['Confidence'] * 10 ** 2) / 10 ** 2
                result[index]['mouth_open'] = {}
                result[index]['mouth_open']['value'] = mouth_open
                result[index]['mouth_open']['confidence'] = math.floor(details['MouthOpen']['Confidence'] * 10 ** 2) / 10 ** 2
                result[index]['beard'] = {}
                result[index]['beard']['value'] = beard
                result[index]['beard']['confidence'] = math.floor(details['Beard']['Confidence'] * 10 ** 2) / 10 ** 2
            statement="success"
        else:
            result = None
            statement = "No Face is found in an image"

    except Exception as e :
        result=None
        statement="Something went wrong"

    finally:
       return result,statement

#
# if __name__ == '__main__':
#     get_analysis('grp.jpg')

