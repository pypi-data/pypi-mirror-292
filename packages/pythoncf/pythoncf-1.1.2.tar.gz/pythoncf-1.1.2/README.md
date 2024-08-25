# pythoncf

`pythoncf` is the perfect tool for Codeforces enthusiasts who prefer to stay nestled in their comfy terminals rather than venturing out into the wilds of the web. Get your Codeforces API data fix without ever leaving your cozy command line setup.

## 🚀 Features

- **User Information**: Retrieve details about a specific Codeforces user.
- **Rating Graph**: Display the rating chart of a user.
- **Contest Information**: Get details about a specific contest.
- **Problem Retrieval**: Fetch all problems or filter by tags.
- **Blog Entries**: View specific blog entries and user blog entries.
- **Rating Changes**: Get the rating changes for a contest.
- **User Status**: Retrieve submission status of a user in a contest.
- **Contest Status**: Get the status of submissions in a contest.
- **User Comparison**: Compare two users' information.

## 📦 Installation

To install `pythoncf`, use `pip`:

```bash
pip install pythoncf
```
### Additional Requirements

For the user comparison feature, you need to install **GNUplot**. You can install it with:

- **Ubuntu/Debian:**

    ```bash
    sudo apt-get install gnuplot
    ```

- **macOS (using Homebrew):**

    ```bash
    brew install gnuplot
    ```

- **Windows:**

    Download and install GNUplot from the [official website](http://www.gnuplot.info/).


## 🛠️ Usage

The following examples illustrate the usage of `pythoncf`:

- **Display user details:**

    ```bash
    pythoncf -userinfo ImFire
    ```
![](https://raw.githubusercontent.com/Sudhir878786/pythoncf/master/images/1.png)

- **Display rating chart of a user:**

    ```bash
    pythoncf -graph ImFire
    ```
![](https://raw.githubusercontent.com/Sudhir878786/pythoncf/master/images/2.png)

- **Get details of a specific contest:**

    ```bash
    pythoncf -contestinfo 1901
    ```
![](https://raw.githubusercontent.com/Sudhir878786/pythoncf/master/images/3.png)

- **Retrieve all problems:**

    ```bash
    pythoncf -prob
    ```
 ### View available commands for prob. 
- `list n`: List `n` problems. 

 ![](https://raw.githubusercontent.com/Sudhir878786/pythoncf/master/images/4.png)

- `listc cid`: List problems of contest ID `cid`. 

![](https://raw.githubusercontent.com/Sudhir878786/pythoncf/master/images/5.png)

- `listn name`: View problem details specified by name. 

![](https://raw.githubusercontent.com/Sudhir878786/pythoncf/master/images/6.png)

- **Retrieve problems with a specific tag:**

    ```bash
    pythoncf -prob --tag dp
    ```


- **Get rating changes for a contest:**

    ```bash
    pythoncf -ratingchange 1901
    ```
![](https://raw.githubusercontent.com/Sudhir878786/pythoncf/master/images/7.gif)

- **Get rating changes for a contest with a specific handle:**

    ```bash
    pythoncf -ratingchange 1901 --handle ImFire
    ```

![](https://raw.githubusercontent.com/Sudhir878786/pythoncf/master/images/8.png)

- **Get submissions of a specified user:**

    ```bash
    pythoncf -submission ImFire
    ```
![](https://raw.githubusercontent.com/Sudhir878786/pythoncf/master/images/9.png)

- **Get submissions with pagination:**

    ```bash
    pythoncf -submission ImFire --fr 1 --count 10
    ```

- **Get contest submissions:**

    ```bash
    pythoncf -submission 1901
    ```
![](https://raw.githubusercontent.com/Sudhir878786/pythoncf/master/images/10.gif)

- **Get contest submissions with pagination:**

    ```bash
    pythoncf -conteststatus 1901 --fr 1 --count 10
    ```

- **Compare two users:**

    ```bash
    pythoncf --compare ImFire Petr
    ```
![](https://raw.githubusercontent.com/Sudhir878786/pythoncf/master/images/11.png)

## 📜 Arguments

| Argument                                      | Description                                           |
|-----------------------------------------------|-------------------------------------------------------|
| `-userinfo`, `--user <HANDLE>`                | Display user details.                                 |
| `-graph`, `--graph <HANDLE>`                  | Display the rating chart of a user.                   |
| `-contestinfo`, `--contest <CONTEST ID>`      | Get details of a contest.                             |
| `--gym`                                       | Optional argument to list gym contests (use with `-contestinfo`). |
| `-prob`, `--problem`                          | Retrieve all problems.                                |
| `--tag <TAG>`                                 | Tag of problems to retrieve.                          |
| `-ratingchange`, `--ratingchange <CONTEST ID>`| Get rating changes for a contest.                     |
| `--handle <HANDLE>`                           | Specify a handle for rating change queries.           |
| `-submission`, `--userstatus <HANDLE>`        | Get submissions of a specified user.                  |
| `--fr <FROM>`                                 | 1-based index of the first submission to return.      |
| `--count <COUNT>`                             | Number of returned submissions.                       |
| `-conteststatus`, `--cstatus <CONTEST ID>`    | Get contest submissions.                              |
| `--compare <USER1 USER2>`                     | Compare two users.                                    |

## Planned Features (*Working on it*)

- `-allblog`, `--blog` `<BLOG ID>`: View a specific blog entry.
- `-userblog`, `--userblog` `<HANDLE>`: Get blog entries of a user.
- `--login` `<USERNAME>` `<PASSWORD>`: Manage login credentials. 
- `--submit` `<PROBLEM ID>` `<SOLUTION FILE>`: Submit solutions to problems. 
- `--render` `<PROBLEM ID>`: Improve rendering of problem statement. 


## 📞 Facing Issue ??

Sudhir Sharma:  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sudhirsharma87)  
[![Gmail](https://img.shields.io/badge/Email-D14836?style=flat&logo=gmail&logoColor=white)](mailto:sudhirsharma34567@gmail.com)

## 🤝 Contributing

Contributions are welcome! If you have suggestions or improvements, please submit a pull request or open an issue.

## 📝 License
This project is licensed under the **MIT License**. See the [LICENSE](https://github.com/Sudhir878786/pythoncf/LICENSE) file for details.