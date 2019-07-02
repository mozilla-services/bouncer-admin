# bouncer-admin
The admin interface for https://github.com/mozilla-services/go-bouncer/.

---
#### Requirements
|         |            |
| ------------- |:-------------:|
 | docker | 18.09.2 |
| mysql  | 5.6     |
---
## How to get started

```sh app.sh MYSQL_LOGIN```
> replace ```MYSQL_LOGIN``` with whatever parameter you use to connect to mysql with read and write privileges (eg. ```sh app.sh -u root -p```)

Run ```docker exec -it local-nazgul pytest``` in a separate terminal to test the code

That's it! Go to [0.0.0.0:5000](0.0.0.0:5000/)