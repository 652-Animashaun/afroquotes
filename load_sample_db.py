import csv
from afroquotes.models import *
from afroquotes.serializers import *

# To load db with sample data from csv, activate environment and run command
# python manage.py shell
# inside the shell run command 
# exec(open('load_sampledb.py').read())

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

def read_csv(filename):
	serializer = QuotesSerializer()
	userializer = CreateUserSerializer()
	print(users)
	

	# create users

	for user in users.items():
		print(user[1])
		print(type(user[1]))
		userializer = CreateUserSerializer(data=user[1])
		userializer.is_valid(raise_exception=True)
		userializer.save()



	# load csv

	with open(filename, 'r') as filter_file:
		csv_r = csv.reader(filter_file, delimiter=",")
		quotes = []
		next(csv_r)
		for f in csv_r:
			artist = f[2].strip()
			song = f[3].strip()
			quote = f[1].strip()
			contributor = f[6] if f[6] in list(users.keys()) else "anmshmz@gmail.com"
			contributor = User.objects.get(email=contributor)

			if quote is not '' and artist is not '' and song is not '':

				data = {
							"quote": quote,
							"artist": artist,
							"song":song,
							"contributor":contributor
						}

				print(data)

			# serializer = QuotesSerializer(data)
				quote = Quote(**data)
				quote.save()

			# quotes.append(data)

read_csv("afroquotes/afroquotes_dumps.csv")

#if __name__ == '__main__':
#	read_csv("afroquotes_dumps.csv")
