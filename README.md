
# Online Judge Backend

This is the backend repository for my Online Judge Plaform which allows users to practice,learn their DSA skills and praticipate in contests.

Implemented via DjangoRestFramework and uses Postgres for the Database you can also look at the frontend at this [repo](https://github.com/Shlok-Agarwal-7/OJ-Frontend)

The backend is hosted on an EC2 instance on AWS and the frontend is hosted on Vercel the live project is live at [link](https://oj-frontend-tawny.vercel.app/)

## Demo

Link to the demo video of the project [Demo](https://www.loom.com/share/d3c534d2aad2441fa076b5dcb583e33a?sid=14ebe362-b710-4f96-8117-905dc8df8962)

## Features

- Syntax Higlighted Code Editor for `C++` `Java` `Python`
- Problem Tag Filtering and search functionalities 
- Praticipation in Live Contests and Live Leaderboards to gain   points 
- AI Hint Help for solving problems  
- Mentor and Student roles with responsibilites and actions 
- Run & Submit Code and view Submissions 
- Mentor can do CRUD operations on problems and Create and manage Contests

## Run Locally

This project uses **Docker Compose** for easy setup and deployment. Follow the steps below to get it up and running on your local machine.

### Requirements

Before you begin, make sure you have the following installed:

- [Docker](https://docs.docker.com/get-started/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Steps to Run the Project

#### 1. Clone the Repository

```bash
git clone https://github.com/Shlok-Agarwal-7/Online-Judge.git
cd Online-Judge
```

#### 2. Create Environment Variables 

- Copy the .env.example file and declare your env variables in a `.env` file 

#### 3. Build and Start the Containers
Use Docker Compose to build and run all services:

```bash
docker-compose up --build
```

This will build all the Docker images and start all the services defined in docker-compose.yml

#### 4. PORT's to be aware of 

Once the services are up, the server will run on PORT **8000** to access the pgadmin panel go to 

```bash
http://localhost:5432
```

#### 5. Stopping the Application
To stop all running containers:

```bash
docker-compose down
```
This will stop and remove containers, networks, and volumes created by up.

#### 6. Cleaning Up (Optional)
To remove all containers, networks, and volumes (including persistent data):

```bash
docker-compose down -v
``` 
## Contributing

Contributions are always welcome!



