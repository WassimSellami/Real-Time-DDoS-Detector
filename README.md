# DDoS Traffic Classification and Mitigation System

To run the project open Docker then run the following command:
```
docker compose up --build
```
to open the frontend, open your browser and navigate to http://localhost:5000
and the backend will be running on http://localhost:3000

to test connectivity between the frontend and backend, open the frontend container terminal then run the following command:
```
ping backend
```

or from the backend container terminal run the following command:
```
ping frontend
```
if you want to test the filter go to sniffer_controller.py file line 134 then change the label to BENIGN then run the project again.anything that you ping from the backend will be filtered.

