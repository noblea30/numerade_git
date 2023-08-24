from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import string

# Step 1: Load data from files
def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            return file.read().splitlines()
        except:
            print("oops, can't do it", file_path)
            with open(file_path, 'r',encoding='utf-8') as file:
                return file.read().splitlines()
            exit(0)
            return [""]


import re

def sanitize_text(text):
    # Remove punctuation
    #return text
    text = text.translate(str.maketrans('', '', string.punctuation))
    #text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    #text = text.replace('\u200B', '')
    # Convert to lowercase
    text = text.lower()

    # Remove numerical digits
    text = ''.join([char for char in text if not char.isdigit()])

    # Remove multiple whitespaces and leading/trailing whitespaces
    text = ' '.join(text.split())

    # Return the sanitized text
    return text

def test_data(str, threshold):
    new_strings_vectorized = loaded_vectorizer.transform([str])
    probabilities = loaded_model.predict_proba(new_strings_vectorized)
    #print(probabilities)

    ret = ""
    if probabilities[0][0] <threshold:
        #print("take", probabilities[0])
        ret = "take"
    else:
        #print("skip", probabilities[0])
        ret = "skip"
    return ret

take_data = load_data('take.txt')
skip_data = load_data('skip.txt')

# Step 2: Prepare the data
all_data = take_data + skip_data
labels = ['take'] * len(take_data) + ['skip'] * len(skip_data)
all_data = [sanitize_text(x) for x in all_data]
# Step 3: Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(all_data, labels, test_size=0.01, random_state=42)  #test_size was .2 and it worked.  changed to .01 to allow more training.
#print("xtrain",X_train)
#print("xtest",X_test)
#print("ytrain",y_train)
#print("ytest",y_test)
# Step 4: Vectorize the text data
vectorizer = CountVectorizer()
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Step 5: Train the model
model = LogisticRegression(max_iter=100)
model.fit(X_train_vectorized, y_train)

# Step 6: Evaluate the model
accuracy = model.score(X_test_vectorized, y_test)
print("Accuracy:", accuracy)

# Step 7: Save the model
joblib.dump(model, 'model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
print("Model saved.")

# Step 8: Use the saved model to predict new strings
loaded_model = joblib.load('model.pkl')
loaded_vectorizer = joblib.load('vectorizer.pkl')
new1 = 'An open box of maximum volume is to be constructed from a 10 ft by 12 ft piece of sheet metal by cutting equal squares from the corners and turning up the sides. What are the dimensions of the box? Remember: the volume of a box is X W X h Round to tenths Alvzcuatlecol'
new2 = 'Find the volume of the solid that lies within the sphere x2+y2+z2=9, above the xy plane, and outside the cone z=7sqrt(x2+y2)'

new_strings = [new1, new2]
new_strings_vectorized = loaded_vectorizer.transform(new_strings)
predictions = loaded_model.predict(new_strings_vectorized)

# for string, prediction in zip(new_strings, predictions):
#     print(f"String: {string} | Prediction: {prediction}")


new_strings_vectorized = loaded_vectorizer.transform(take_data)
probabilities = loaded_model.predict_proba(new_strings_vectorized)
#print("take probablilities................................")
#print(probabilities)

new_strings_vectorized = loaded_vectorizer.transform(skip_data)
probabilities = loaded_model.predict_proba(new_strings_vectorized)
#print("skip probablilities.............................")
#print(probabilities)
#print("-----------------------")
#print(X_test[0])



# exit(0)
# min = 1
# max = 0
# thresh = .5 #.258
# total = 0
# taken = 0
# for x in X_test:
#     val = test_data(x,thresh)
#     if val > max:
#         max = val
#
#     if val < thresh:
#         taken +=1
#     total +=1
# print("percent right", taken / total)
# taken = 0
# total = 0
#
# type1 = 0
# type2 = 0
# take = 0
# skip = 0
#
# for i in range(len(X_test)):
#     if y_test[i] == "take":
#         val = test_data(X_test[i], thresh)
#
# exit(0)
# for x in y_test:
#     val = test_data(x, thresh)
#     if val < thresh:
#         taken +=1
#         #print(val, thresh)
#     total +=1
#     if val < min:
#         min = val
#
# print(max, min)
#
# print("percent bad",taken / total )
#
#
# for x in X_test:
#     print("X-test:", x)
# for y in y_test:
#     print("Y-test:", y)

#print the scores
thresh = .35
#print("take")
for i in range(len(X_test)):
    if y_test[i] == "take":
        val = test_data(X_test[i], thresh)
#print("skip")
for i in range(len(X_test)):
    if y_test[i] == "skip":
        val = test_data(X_test[i], thresh)


#matrix data:
#          real
#  want         don't want
#  Take         Type2
#  Type1         Skip


result = [[0,0],[0,0]]
for i in range(len(X_test)):
    val = test_data(X_test[i], thresh)
    #print(".",y_test[i], ".", val,".")
    if y_test[i] == "take" and val =="take":
        result[0][0] += 1
    if y_test[i] == "take" and val =="skip":
        result[1][0] += 1
    if y_test[i] == "skip" and val =="take":
        result[0][1] += 1
    if y_test[i] == "skip" and val =="skip":
        result[1][1] += 1

print(result)

print(result[0][0]/(result[0][0] + result[1][0]),result[1][1]/(result[1][1] + result[0][1]) )
