import requests
import csv
import sys
import time

apikey = "b985000626e44905211bdcbc86373e48"
root = "https://api.themoviedb.org/3/"
#key = name, value = id
actor_metadata = dict()

#key = name; value = release date, id
movie_ids = dict()

#key = name; value = id, actor names
movie_credits = dict()

#key = a1&a2, value = weight
edgelist = dict()


#gets actor name and their id, stores it in actor_metadata
def read_in_ids(file_name):
	with open(file_name,mode = 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			name = row['name']
			a_id = row['id']
			actor_metadata[name] = a_id

#need movie, release date to get id

def read_in_movies(file_name):
	#reading in movie files
	with open(file_name,mode = 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			r_date = row['Release Date'].strip()
			#print(r_date)
			year = r_date.split("-")[0]
			#print(year)
			if int(year) > 2018 and int(year) < 2022:
				title = row['Movie']
				info = list()
				info.append(year)
				movie_ids[title] = info

#get movie id, return -1 if not found
def get_movie_ids(name, a_id):
	people_credits = f"person/{a_id}/movie_credits?api_key={apikey}&language=en-US"
	r = requests.get(root+people_credits).json()

	try:
		credits = r['cast']
		if not credits:
			print("Credits is empty")
			return False
		for c in credits:
			try:
				release_date = c['release_date']
				year = int(release_date.split("-")[0])
			except KeyError:
				pass
				#print("Release date doesn't exist")
			except ValueError:
				pass
				#print("Error fetching the year: " + str(release_date))
			else:
				title = c['title']
				if title in movie_ids.keys():
					value = movie_ids[title]
					if len(value) == 1:						
						#print(title)
						#print(f"Release Date: {year}")
						if year > 2017 and year < 2022:
							#print("Updated")
							m_id = c['id']
							value.append(m_id)
							movie_ids.update({title:value})
						#print()
						#time.sleep(3)

	except KeyError:
		print("Key Error: r['cast'] doesn't exist")
		return False
	return True


def form_movie_credits(m_id):
	movie_credits = f"movie/{m_id}/credits?api_key={apikey}&language=en-US"
	r = requests.get(root + movie_credits).json()
	cast = set()
	try:
		for actor in r['cast']:
			a_id = actor['id']
			if str(a_id) in actor_metadata.values():
				for name, num_id in actor_metadata.items():
					if str(a_id) == num_id:
						cast.add(name)
						break
		#print(f"Checked cast for {m_id}: {str(cast)}")
	except:
		print("Unable to retrieve cast")
		return False
	else:
		return cast

def create_moviecred_csv(new_credits):
	with open ('movie_credits.csv', mode = 'w') as csvfile:
		cred_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		cred_writer.writerow(['Movies','Actors'])
		for movie in new_credits:
			cred_writer.writerow([movie, new_credits[movie]])

def form_links(new_credits):
	for movie in new_credits:
		cast = new_credits[movie]
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
	#reading in files
	#userinput = input("Enter in file name (actors): ")
	read_in_ids("actors.csv")
	read_in_movies("movies_2021.csv")
	read_in_movies("movies_2020.csv")
	read_in_movies("movies_2019.csv")

	for actor_name, a_id in actor_metadata.items():
		get_movie_ids(actor_name,a_id)

	new_movieids = {movie:info for (movie,info) in movie_ids.items() if len(info) == 2}
	

	for movie in new_movieids:
		info = new_movieids[movie]
		m_id = info[1]
		cast = form_movie_credits(m_id)
		movie_credits[movie] = cast

	new_credits = {movie:info for (movie,info) in movie_credits.items() if len(info) > 1}
	new_credits = {movie:list(info) for (movie,info) in new_credits.items()}
	new_credits = {movie:sorted(info) for (movie,info) in new_credits.items()}

	create_moviecred_csv(new_credits)
	#form_links(new_credits)
	#create_edgelist()


	"""
	#check
	counter = 1
	for movie, info in new_movieids.items():
		print(f"[{counter}] {movie}: [{str(info)}]")
		counter += 1

	counter = 1
	for m, c in new_credits.items():
		print(f"[{counter}] {m}: [{str(c)}]")
		counter +=1
	"""

	
	
	

	


if __name__ == '__main__':
	main()