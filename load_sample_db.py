import csv
import random
from datetime import datetime
from afroquotes.models import Quote, Annotation, User  # Replace 'your_app' with the actual app name
from afroquotes.serializers import QuotesSerializer, CreateUserSerializer, QResponseSerializer  # Replace with actual import paths
from faker import Faker
import logging

faker = Faker()

def read_csv(filename):
	# Assume users is a predefined dictionary with user data
	users = {
			"prosperonyekwere4@gmail.com":{
				"password":"pass",
				"username":"prosper56",
				"email":"prosperonyekwere4@gmail.com",
				"first_name": "prosper",
				"last_name":"Onye",
				
			},
			"anmshmz@gmail.com":{
				"password":"pass",
				"username":"shaun88",
				"email":"anmshmz@gmail.com",
				"first_name": "shaun",
				"last_name":"shaun88",
				
			},
			"perelaignite24@gmail.com":{
				"password":"pass",
				"username":"promise45",
				"email":"perelaignite24@gmail.com",
				"first_name": "promise",
				"last_name":"prom",
				
			}

	}

	# Create users
	for user in users.items():
		print(user[1])
		print(type(user[1]))
		try:
			userializer = CreateUserSerializer(data=user[1])
			userializer.is_valid(raise_exception=True)
			userializer.save()
		except:
			pass

	# Load CSV
	with open(filename, 'r') as filter_file:
		csv_r = csv.reader(filter_file, delimiter=",")
		quotes = []
		next(csv_r)
		for f in csv_r:
			artist = f[2].strip()
			song = f[3].strip()
			quote_text = f[1].strip()
			annotation_text = f[4].strip()  # Assuming the annotation is in the 5th column
			contributor_email = f[6] if f[6] in list(users.keys()) else "anmshmz@gmail.com"
			contributor = User.objects.get(email=contributor_email)

			if quote_text and artist and song:
				quote_data = {
					"quote": quote_text,
					"artist": artist,
					"song": song,
					"contributor": contributor
				}
				quote = Quote(**quote_data)
				logging.info(f"CREATED QUOTE:   : {quote_data}")
				quote.save()

				# Create annotation
				if len(annotation_text) > 5:

					annotation_data = {
						"annotation": annotation_text,
						"annotator": contributor,
						"annotated": quote,
						"verified": False,
						"annotation_view_count": random.randint(0, 100),
						"last_viewed": faker.date_time_this_year().strftime('%Y-%m-%d %H:%M:%S'),
						"timestamp": datetime.now(),
					}
					annotation = Annotation(**annotation_data)
					annotation.save()
					logging.info(f"CREATED QUOTE:   : {annotation_data}")

					# Add approvers
					approvers = User.objects.filter(email__in=list(users.keys()))
					for approver in approvers:
						annotation.approvers.add(approver)
					annotation.save()


read_csv("afroquotes/afroquotes_dumps.csv")



# def main():
# 	print("RUnnig Thangs")
# 	logging.info("RUNNING THANGS::::::::")

# 	quotes = Quote.objects.all()
# 	logging.info(f"FOUND TOTAL QUOTES:   : {len(quotes)}")

# 	quotes = [q.serialize() for q in quotes]
# 	logging.info(f"FOUND TOTAL QUOTES:   : {quotes[:6]}")
# 	count = 0
# 	for i in quotes:
# 		annotation = i["annotation"]["annotation"] 
# 	# 	logging.info(f"FOUND BLANK ANNOTATION FOR QUOTE:   : {annotation}")
# 		if annotation == '':
# 			count += 1
# 			snippets = {"id": {i["id"]}, "annotation":{**i["annotation"]} }
# 			logging.info(f"FOUND BLANK ANNOTATION FOR QUOTE:   : {snippets}")
# 			Annotation.objects.get(id=i["id"]).delete()
# 	# 		# logging.info(f"REMOVED BLANK ANNOTATION FOR QUOTE:   : {snippets}")
# 	logging.info(f"TOTAL BLANK ANNOTATION REMOVED:   : {count}")
# main()

			# annotation = Annotation.objects.get(id=i["id"]).delete()
# if __name__ == '__main__':
# 	main()

