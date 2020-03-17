-- sudo mysql -u root qiank < 20200316T230600-create_tables.sql
create table users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       username VARCHAR(255) NOT NULL,
       password VARCHAR(255) NOT NULL,
       email VARCHAR(255) NOT NULL
);
   
   
create table channels (
      id INT AUTO_INCREMENT PRIMARY KEY,
      channelname VARCHAR(255) NOT NULL UNIQUE,
      creatorid INT,
      FOREIGN KEY(creatorid) REFERENCES users(id)
);
   
create table messages (
      id INT AUTO_INCREMENT PRIMARY KEY,
      content TEXT,
      channelid INT,
      messageid INT,
      creatorname VARCHAR(255),
      userid INT
);
