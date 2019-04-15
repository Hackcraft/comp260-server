import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from Data_Handlers.Database import Database

db = Database("127.0.0.1", "root", "", "mud")

# Setup
db.Commit("CREATE TABLE IF NOT EXISTS test_tab ( `id` INT NOT NULL );", None)

def FetchCallBack(data):
    assert len(data) > 1

def CommitCallback(success):
    assert success == True
    db.Fetch("SELECT * FROM test_tab", FetchCallBack)

db.Commit("INSERT INTO test_tab(id) VALUES(%s)", (1010,), CommitCallback)

