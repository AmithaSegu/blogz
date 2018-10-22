from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'root'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    detail = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
    def __init__(self,title,detail,ownerid):
        self.title=title
        self.detail=detail
        self.ownerid=ownerid

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='ownerid')
    
    def __init__(self,username,password):
        self.username=username
        self.password=password

def input_empty(name):
    if len(name)>0:
        return True
    else:
        return False

def length_validation(name1):
    if (len(name1)>=3 and len(name1)<=20):
        return True
    else:
        return False

def space_validation(name3):
    if ' ' in  name3:
        return False
    else:
        return True

@app.route('/', methods=['POST','GET'])
def index():
    user_id=User.query.all()
    return render_template('index.html',users=user_id)

@app.route('/single_user', methods=['POST','GET'])
def single_user():
    if request.method=='GET':
        if request.args:
            user_name=request.args.get("id")
            user_id=User.query.filter_by(username=user_name).first()
            blogs=Blog.query.filter_by(owner_id=user_id.id).all()
            return render_template("main_blog_page.html",blogs=blogs)
    return render_template("main_blog_page.html")


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','index','blog_page','single_user']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if username=="" and password=="":
            flash("Please enter valid username and password")
            return render_template('login.html')
        else:
            user= User.query.filter_by(username=username).first()
            if user==None:
                flash("USER IS NOT REGISTERED OR ENTERED INCORRECT USERNAME")
            #return redirect('/login')
                return render_template('login.html')
            if user and user.password != password:
                flash("PASSWORD IS INCORRECT")
            #return redirect('/login')
                return render_template('login.html')
            if user and user.password == password:
                session['username']=username
                flash("LOGGED IN")
            #return redirect('/newpost')
                return render_template('new_post_page.html')
    else:				
        return render_template('login.html')

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        verify_password=request.form['verify_password']
        username_error=''
        password_error=''
        veri_password_error=''
        
        if input_empty(username)==False:
            username_error="Feild is empty.Please enter valid data"
        elif length_validation(username)==False:
            username_error="Username should be in the range of 3 to 20 chars"
        elif space_validation(username)==False:
            username_error="Username has spaces. Please remove and re-enter a valid username"
        else:
            username_error=''
            
        if input_empty(password)==False:
            password_error="Feild is empty.Please enter valid password"
        elif length_validation(password)==False:
            password_error="Password should be in the range of 3 to 20 chars"
        elif space_validation(password)==False:
            password_error="Password has spaces. Please remove and re-enter a valid password"
        else:
            password_error=''
    
        if input_empty(verify_password)==False:
            veri_password_error="Feild is empty.Please enter valid password"
        elif length_validation(verify_password)==False:
            veri_password_error="Password should be in the range of 3 to 20 chars"
        elif space_validation(verify_password)==False:
            veri_password_error="Password has spaces. Please remove and re-enter a valid password"
        else:
            if verify_password==password:
                veri_password_error=''
            else:
                veri_password_error="Password and Verify password do not match. Please re-enter"

        if (not password_error and not username_error and not veri_password_error):
            existing_user = User.query.filter_by(username=username).first()    
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                flash("USER NAME ALREADY EXISTS")
                return('/signup')
        else:
            return render_template('signup.html',username=username, password='', verify_password='', username_error=username_error,password_error=password_error,veri_password_error=veri_password_error)

    return render_template('signup.html')

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/login')

	
@app.route('/blog', methods=['POST','GET'])
def blog_page():
    if request.method=='GET':
        if request.args:
            blog_id = request.args.get("id")
            blog = Blog.query.get(blog_id)
            return render_template('blog_page.html',blog=blog)        
    blogs= Blog.query.all()
    return render_template('main_blog_page.html',blogs=blogs)        

@app.route('/newpost', methods=['POST','GET'])
def new_blog_page():
    title_error=""
    detail_error=""

    #owner_id = User.query.filter_by(username=session['username']).first()
    if request.method=='GET':
        return render_template('new_post_page.html')

    if request.method=='POST':
        titles = request.form['title_blog']
        details = request.form['detail']
        
        if titles == "":
            title_error="PLEASE ENTER VALID TITLE"
            return render_template('new_post_page.html',title_error=title_error,detail_error=detail_error)
        
        if details == "":
            detail_error="PLEASE ENTER A VALID DETAIL"
            return render_template('new_post_page.html',title_error=title_error,detail_error=detail_error)
        
        if title_error=="" and detail_error=="":
            owner=User.query.filter_by(username=session['username']).first()
            title_detail = Blog(titles,details,owner)
            db.session.add(title_detail)
            db.session.commit()
            id = title_detail.id
            #blog_user= Blog.query.filter_by(ownerid=owner).all()
            #return render_template('blog_page.html',titles=titles,details=details)
            return redirect('/blog?id={0}'.format(id))

        return render_template('new_post_page.html',title_error=title_error,detail_error=detail_error)
    
if __name__ =='__main__':
    app.run()