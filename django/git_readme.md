Git global setup
git config --global user.name "olexandr lets"
git config --global user.email "o.lec@dir.gov.ua"

Create a new repository
git clone https://gitlab.dir.gov.ua/letsolexandr/edoc.git
cd edoc
touch README.md
git add README.md
git commit -m "add README"
git push -u origin master

Push an existing folder
cd existing_folder
git init
git remote add origin https://gitlab.dir.gov.ua/letsolexandr/edoc.git
git add .
git commit -m "Initial commit"
git push -u origin dev
git push -u origin master


Push an existing Git repository
cd existing_repo
git remote rename origin old-origin
git remote add origin https://gitlab.dir.gov.ua/letsolexandr/edoc.git
git push -u origin --all
git push -u origin --tags


git remote set-url dir https://letsolexandr:_txvouzxGWv_bGWZ4LA2@gitlab.dir.gov.ua/letsolexandr/edoc.git