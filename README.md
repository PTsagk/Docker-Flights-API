# YpoxreotikiErgasia23_E20164_Tsagkouris_Panagiotis


## Διαδικασία Εκκίνησης
Αφού κατεβάσουμε ή κάνουμε clone το repository πηγαίνουμε στο command prompt και κάνουμε cd στην τοποθεσία που έχουμε τα αρχεία.
```sh
cd path_to_project
docker-compose -p "container_name" up
```
Μετά από αυτές τις εντολές το container θα τρέχει ενώ το mongodb θα ακούει στην πόρτα **27017** και το python web service στην πόρτα **5000**

## Οδηγίες Χρήσης

Ακολουθούν οι οδηγίες χρήσης καθώς και παραδείγματα για την χρήση του κάθε endpoint. Θα ξεκινήσουμε πρώτα με τα endopoint που αφορούν τον χρήστη και ύστερα αυτά που αφορούν τον διαχειριστή (εκτός από αυτά που αφορούν και τους δύο οπότε αναφέρονται μαζί με τα endpoint του χρήστη).

## /register (POST)
Το endpoint register αφορά την δημιουργεία λογαριασμού κάποιου χρήστη. Στο body του request θα πρέπει να δοθούν οι παράμετροι σε μορφή **string**:
- **username** (Όνομα Χρήστη)
- **surname** (Επώνυμο Χρήστη)
- **email** (Email)
- **password** (Κωδικός)
- **birthDate** (Ημερομηνία Γέννησης)
- **country** (Χώρα Καταγωγής)
- **passportNumber** (Αριθμός Διαβατηρίου)

#### Παράδειγμα μορφής body: 
```json
{
	"username":"panagiotis",
	"surname":"tsagouris",
	"email":"tsagouris500@gmail.com",
	"password":"panagiotis123",
	"birthDate":"2002",
	"passportNumber":"1232131412",
	"country":"greece",
}
```

Αν όλα πάνε καλά ο server θα απαντήσει με το μήνυμα **"Account created succesfully"** και status code **200**.
## /login (POST)
> **Μπορεί να χρησιμοποιηθεί και από τον  διαχειριστή.**

Το endpoint login αφορά την είσοδο του χρήστη ή του διαχειριστή στον λογαριασμό του. Παίρνει σαν παραμέτρους στο body το **email** και το **password**. Αν τα στοιχεία είναι σωστά (δηλαδή υπάρχουν στην βάση δεδομένων) τότε ο server θα στείλει ένα cookie με τιμή το _id του χρήστη στην βάση δεδομένων.

## /logout (GET)
> **Μπορεί να χρησιμοποιηθεί και από τον  διαχειριστή.**

Το endpoint αυτό αφορά την έξοδο του χρήστη. Δεν χρειάζονται παράμετροι στο body. Ο server στέλνει σαν απάντηση ένα cookie με 0 χρόνο λήξης και καινή τιμή.
## /flights (GET)
> **Μπορεί να χρησιμοποιηθεί και από τον  διαχειριστή.**

Το endpoint αυτό επιστρέφει τις πτήσεις με βάση τις παραμέτρους τις οποίες δίνει ο χρήστης στο query. Τα αποτελέσματα είναι σε ένα array το οποίο περιέχει objects και όπου το κάθε object περιέχει πληρφορίες για την πτήση. Οι παραμέτροι οι οποίες μπορούν να δωθούν είναι:
- **depart**, **destination** και **date**
- **depart** και **destination**
- **date**

#### Παραδείγματα χρήσης και αποτελεσμάτων:
#### ``/flights?depart="Athens"&destination="Italy"&date=20-10-2023``
```json
[
	{
		"_id":{"$oid":  "6494bf4bb7e772787c0c630f"},
		"date":  "20-10-2023",
		"depart_airport":"Athens",
		"destination_airport":  "Italy"
	}
]
```
#### ``/flights?depart="Athens"&destination="Italy"``
```json
[{
	"_id":{"$oid":  "6494bf4bb7e772787c0c630f"},
	"date":  "20-10-2023",
	"depart_airport":  "Athens",
	"destination_airport":  "Italy"
},
{
	"_id":  {"$oid":  "6494c02fb7e772787c0c6310"},
	"date": "20-8-2023",
	"depart_airport":  "Athens",
	"destination_airport":  "Italy"
}]
```

#### ``/flights?date=6-7-2023``
```json
{
	"_id":  { "$oid":  "6494c1ccb7e772787c0c6312" },
	"business_cost":  20,
	"business_count":  5,
	"date":  "6-7-2023",
	"depart_airport":  "Germany",
	"destination_airport":  "Athens",
	"economy_cost":  10, 
	"economy_count":  10
}
```

## /flights/information (GET)
Αυτό το endpoint παίρνει σαν query parameter το **flight_id** το οποίο πρέπει να έχει σαν τιμή κάποιo _id πτήσης για να εμφανίσει περισσότερες πληρφορίες για αυτή την πτήση.
#### Παράδειγμα:
#### ``/flights/information?flight_id=6494c02fb7e772787c0c6310``
#### Αποτέλεσμα
```json
[
	{
		"_id": { "$oid":  "6494c02fb7e772787c0c6310" },
		"business_cost":  20,
		"business_count":  5,
		"date":  "20-8-2023",
		"depart_airport":  "Athens",
		"destination_airport":  "Italy",
		"economy_cost":  10,
		"economy_count":  10 
	}
]
```
## /reservations/create (POST)
Αυτό το endpoint χρησιμοποιείται για την δημιουργεία κρατήσεων. Παίρνει στο body τις παραμέτρους:
- **username** (Όνομα Χρήστη)
- **surname** (Επώνυμο Χρήστη)
- **passportNumber** (Αριθμός Διαβατηρίου)
- **birthDate** (Ημερομηνία Γέννησης)
- **email** (Email)
- **reservationType**(Τύπος κράτησης ecnomy ή business)
#### Παράδειγμα μορφής body: 
```json
{
	"username":"panagiotis",
	"surname":"tsagouris",
	"passportNumber":"1232131412",
	"birthDate":"2002",
	"email":"tsagouris500@gmail.com",
	"reservationType":"economy"
}
```
Επιπλέον χρειάζεται να δηλωθεί και το **flight_id** σαν query parameter για να δείξει σε ποια πτήση θέλει να γίνει η κράτηση. π.χ.
 #### ``/reservations/create?flight_id=6494c02fb7e772787c0c6310``
 Αν όλα πάνε καλά ο server θα απαντήσει με το μήνυμα **"Reservation Completed"** και status code **200**.
## /reservations (GET)
Αυτό το endpoint δεν παίρνει παραμέτρους και επιστρέφει τα **_id** των πτήσεων στις οποίες έχει κάνει κράτηση ο χρήστης καθώς και το **_id** της κράτησης π.χ.
```json
{
	"_id":  {
		"$oid":  "6494ca21b7e772787c0c6314"
	},
	"flight_id":  "6494c02fb7e772787c0c6310"
}
```

## /reservations/details (GET)
Αυτό το endpoint παίρνει ως query parameter το **reservation_id** και επιστρέφει πληροφορίες σχετικά με κάποια συγκεκριμένη κράτηση.
#### Παράδειγμα
**``/reservations/details?reservation_id=6494ca21b7e772787c0c6314``** 
#### Αποτέλεσμα
```json
[
	{
		"birth_date":  "2002",
		"email":  "tsagouris500@gmail.com",
		"flight_id":  "6494c02fb7e772787c0c6310",
		"passport_number":  "1232131412"
		"reservation_type":  "economy",
		"surname":  "tsagouris",
		"user_id":  "6494ca0ab7e772787c0c6313",
		"username":  "panagiotis"
	},
	{
		"date":  "20-8-2023",
		"depart_airport":  "Athens",
		"destination_airport":  "Italy"
	}
]
```

## /reservations/cancel (DELETE)
Αυτό το endpoint παίρνει σαν query parameter το **reservation_id** και διαγράφει την πτήση π.χ.
#### ``/reservations/cancel?reservation_id=6494ca21b7e772787c0c6314``
Αν όλα πάνε καλά ο server θα απαντήσει με το μήνυμα **"Reservation canceled"** και status code **200**.
## /users/delete (DELETE)
Αυτό το endpoint δεν παίρνει παραμέτρους και διαγράφει τον λογαριασμό του χρήστη (Δεν λειτουργεί για τον διαχειριστή).
#### /users/delete
Αν όλα πάνε καλά ο server θα απαντήσει με τον μήνυμα **"Your account was deleted succesfully"** και status code **200**.
# Endpoints του Διαχειριστή
Ακολουθούν τα endpoints που αφορούν μόνο τον διαχειριστή του συστήματος. Κάποια από τα προηγούμενα endpoints που αφορούσαν τον χρήστη αφορούν και τον διαχειριστή οπότε δεν χρειάζονται να ξαναναφερθούν. Τα στοιχεία σύνδεσης του διαχειριστή είναι:
- email: admin@gmail.com
- password: **admin123**
## /flights/create (POST)
Αυτό το endpoint αφορά την δημιουργεία πτήσης με βάση τα στοιχεία τα οποία παρέχει ο διαχειριστή στο request body. Το body παίρνει τις εξής παραμέτρους:
- **departAirport: string** (Αεροδρόμιο Προέλευσης)
- **destinationAirport: string** (Αεροδρόμιο Προορισμού)
- **date: string** (Ημερομηνία Πτήσης)
- **economyCost: decimal** (Κόστος εισιτηρίου για economy)
- **businessCost: decimal** (Κόστος εισιτηρίου για business)
- **economyCount: integer** (Πλήθος διαθέσιμων economy εισιτηρίων)
- **businessCount: integer** (Πλήθος διαθέσιμων business εισιτηρίων)

#### Παράδειγμα μορφής body: 
```json
{
	"departAirport":"Germany",
	"destinationAirport":"Athens",
	"date":"6-7-2023",
	"economyCost":10.5,
	"businessCost":20,
	"economyCount":10,
	"businessCount":5
}
```
Αν όλα πάνε καλά ο server θα απαντήσει με το μήνυμα **"Flight created successfully"** και status code **200**
## /flights/change_cost (PATCH)
Αυτό το endpoint αφορά την αλλαγή κόστους των εισιτηρίων για την πτήση με το **flight_id** που δίνεται σας query parameter. Επιπλέον πρέπει να δωθεί στο body η νέα τιμή είτε για το εισιτήριο του economy είτε για το εισιτήριο του business είτε και για τα δύο. 
#### Παραδείγματα μορφής body
 **Ενημέρωση του κόστους του economy και του business**
```json
{
	"economyCost":23.7,
	"businessCost":30.3,
}
```
**Ενημέρωση του κόστους μόνο για το economy**
```json
{
	"economyCost":23.7,
}
```
**Ενημέρωση του κόστους μόνο για το business**
```json
{
	"businessCost":30.3,
}
```
#### Παράδειγμα κλήσης του endoint
**``/flights/change_cost?flight_id=6494c02fb7e772787c0c6310``**
Αν όλα πάνε καλά ο server θα απαντήσει με το μήνυμα **"Costs updated successfully"** και status code **200**.
## /flights/delete (DELETE)
Αυτό το endpoint αφορά την διαγραφή μίας πτήσης η οποία δεν έχει κρατήσεις. Χρειάζεται να δωθεί σαν query  parameter το **flight_id**.
#### Παράδειγμα
**``/flights/delete?flight_id=6494c02fb7e772787c0c6310``**
Αν όλα πάνε καλά ο server θα απαντήσει με το μήνυμα **"Flight deleted succesfully"** και status code **200**.
## /flights/admin/info (GET)
Αυτό το endpoint αφορά την εύρεση πληφοροφοριών για μία πτήση καθώς και πληροφορίες για τις κρατήσεις που αφορούν αυτή την πτήση. Χρειάζεται να δωθεί σαν query parameter το **flight_id**.
  #### Παράδειγμα 
 **``/flights/admin/info?flight_id=6494c02fb7e772787c0c6310``**
 #### Αποτέλεσμα
```json
[
	{
		"business_cost":  20,
		"business_count":  5,
		"date":  "20-8-2023",
		"depart_airport":  "Athens",
		"destination_airport":  "Italy",
		"economy_cost":  10,
		"economy_count":  9
	},
	{
		"total business tickets booked":  0,
		"total economy tickets booked":  1,
		"total tickets":  1
		},
	[
		{
			"reservation_type":  "economy",
			"surname":  "tsagouris",
			"username":  "panagiotis"
		}
	]
]
 ```
