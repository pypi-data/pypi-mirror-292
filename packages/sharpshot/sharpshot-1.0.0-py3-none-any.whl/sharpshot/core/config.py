# -*- coding: UTF-8 -*-
import os

# sqlite3 path
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db")
# git project clone file path
project_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "project")
# ignore file pattern
ignore_file = ['*/pom.xml', '*/test/*', '*.sh', '*.md', '*/checkstyle.xml', '*.yml', '.git/*']
# project package startswith
package_prefix = ['com.', 'cn.', 'net.']
# Whether to reparse the class when there is class data in the database
reparse_class = True
