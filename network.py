import requests
import csv
import sys

apikey = "b985000626e44905211bdcbc86373e48"
root = "https://api.themoviedb.org/3/"
actor_metadata = dict()
movie_ids = dict()
edgelist = dict()


#-- Forming actor attribute csv file
#NAME: [ranking(0), star score(1), id(2), birthyear(3), gender(4)]
def read_in_names(file_name):
	with open(file_name,mode = 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			name = row['Name']
			metadata = [row['Ranking'], row['Star Score']]
			actor_metadata[name] = metadata
		 
def get_actor_id(name):
	search = f"search/person?api_key={apikey}&language=en-US&query=\"{name}\"&page=1"
	r = requests.get(root + search).json()
	try:
		results = r['results']

	except:
		print(name + ": " + r['status_message'])
		return -1
	else:
		try:
			for r in results:
				if r['name'].casefold() == name.casefold():
					info = actor_metadata[name]
					a_id = r['id']
					info.append(a_id)
					actor_metadata.update({name:info})
					return a_id
			return -1
		except KeyError as e:
			print("KeyError: " + e)
			return -1

def add_actor_info(name, a_id):
	person_details = f"person/{a_id}?api_key={apikey}&language=en-US"
	r = requests.get(root + person_details).json()
	try:
		birthday = r['birthday']
	except:
		birthday = 'N/A'
	try:
		gender = r['gender']
	except:
		gender = -1
	info = actor_metadata[name]
	info.append(birthday)
	info.append(gender)
	actor_metadata.update({name:info})

def create_actor_att_csv():
	with open ('actor_att.csv', mode = 'w') as csvfile:
		att_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		att_writer.writerow(['Name','Ranking','Star Score','ID','Birthday','Gender'])
		for actor, data in actor_metadata.items():
			att_writer.writerow([actor, data[0], data[1], data[2], data[3], data[4]])


#-- Forming movie edgelist
def read_in_ids(file_name):
	with open(file_name,mode = 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			name = row['Name']
			a_id = row['ID']
			actor_metadata[name] = a_id

def get_movie_id(a_id, name):
	tv_movie_id = 10770
	people_credits = f"person/{a_id}/movie_credits?api_key={apikey}&language=en-US"
	r = requests.get(root+people_credits).json()
	try:
		credits = r['cast']
		if not credits:
			print("Credits is empty")
			return False
		for c in credits:
			try:
				release_date = c['release_date'].split("-")
				year = int(release_date[0])
			except KeyError:
				pass
				#print("Release date doesn't exist")
			except ValueError:
				pass
				#print("Error fetching the year: " + str(release_date))
			else:
				genre_ids = c['genre_ids']
				if year > 2018 and year < 2022 and tv_movie_id not in genre_ids:
					title = c['title']
					#print(title + ", " + str(year))
					if title not in movie_ids.keys():
						info = [c['id'], name]							
						movie_ids[title] = info
					else:
						info = movie_ids[title]
						info.append(name)
						movie_ids.update({title:info})

	except KeyError:
		print("Key Error: r['cast'] doesn't exist")
		return False
	return True

def create_movieID_csv():
	with open ('movie_ids.csv', mode = 'w') as csvfile:
		id_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		id_writer.writerow(['Movies','ID','Actors'])
		for movie in movie_ids:
			if(len(movie_ids[movie]) > 2):
				id_writer.writerow([movie, movie_ids[movie][0], movie_ids[movie][1:]])

def filter_out_movies():
	excluded = set()
	with open('excluded_movies.csv',mode = 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			title = row['Movies']
			excluded.add(title)
	for movie in movie_ids:
		if(len(movie_ids[movie]) <= 2):
			excluded.add(movie)
	excluded = list(excluded)
	for t in excluded:
		if t in movie_ids.keys():
			movie_ids.pop(t)

def form_links():
	for movie in movie_ids:
		info = movie_ids[movie]
		cast = info[1:]
		for i in range(0,len(cast) - 1):
			a1 = cast[i]
			for x in range(i + 1, len(cast)):
				a2 = cast[x]
				link = f"{a1}&{a2}"
				if link not in edgelist.keys():
					edgelist[link] = 1
				else:
					weight = edgelist[link]
					weight += 1
					edgelist.update({link:weight})

def create_edgelist():
	with open ('edgelist.csv', mode = 'w') as csvfile:
		edge_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		edge_writer.writerow(['To','From','Weight'])
		for link in edgelist:
			names = link.split("&")
			a1 = names[0]
			a2 = names[1]
			weight = edgelist[link]
			edge_writer.writerow([a1, a2, weight])

	
def main():
	#reading in names and getting ids]
	choice = int(input("Choose (1) to form attributes or (2) to form edgelist: "))
	if choice == 1:
		user_in = input("Type in the file name: ")
		file_name = f"{user_in}.csv"
		read_in_names(file_name)
		for key in actor_metadata:
			a_id = get_actor_id(key)
			if a_id != -1:
				add_actor_info(key, a_id)
		create_actor_att_csv()

	elif choice == 2:
		user_in = input("Type in the file name: ")
		file_name = f"{user_in}.csv"
		read_in_ids(file_name)
		for name in actor_metadata:
			a_id = actor_metadata[name]
			worked = get_movie_id(a_id,name)

		user_in = int(input("Choose (1) to form movie credits csv, (2) to create edgelist: "))
		if user_in == 1:
			create_movieID_csv()
		elif user_in == 2:
			#key= movie title, value = [ID, actor_name, actor_name...]
			filter_out_movies()
			form_links()
			create_edgelist()

		else:
			print("Exiting...")
			sys.exit()
	else:
		print("Exiting...")
		sys.exit()


if __name__ == '__main__':
	main()

