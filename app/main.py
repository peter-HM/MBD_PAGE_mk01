from enum import unique
from locale import currency
import stat
import uuid
from fastapi import FastAPI, Request, Form, UploadFile, File, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db.database import Base, engine, SessionLocal
from app.models.post import Post
from app.models.user import User
from app.models.project import Project
from app.db.database import get_db

from starlette.middleware.sessions import SessionMiddleware

from pathlib import Path, PurePosixPath
from uuid import uuid4

from sqlalchemy import or_

##### FUNC #######################################################################

def can_edit_or_delete(user: dict, post: Post) -> bool:
    if user["role"] == "mgr":
        return True
    return post.author_id == user["id"]


def send_test_data():
    db= SessionLocal()
    try:
        if db.query(User).count() > 0:
            return
        mgr = User(
            username="mgr1",
            password="1234",
            nickname="Manager One",
            role="mgr",
            avatar_image=""
        )

        user1 = User(
            username="user1",
            password="1234",
            nickname="User One",
            role="user",
            avatar_image=""
        )

        user2 = User(
            username="user2",
            password="1234",
            nickname="User Two",
            role="user",
            avatar_image=""
        )

        db.add_all([mgr, user1, user2])
        db.commit()

        db.refresh(mgr)
        db.refresh(user1)
        db.refresh(user2)

        posts = [
            Post(
                author_id=mgr.id,
                title="관리자 공지 글",
                body="이 글은 관리자가 작성한 공개 공지입니다.",
                url="#",
                image_path="",
                is_public=True,
                cat="notice",
                cat_detail="aws"
            ),
            Post(
                author_id=user1.id,
                title="user1 공개 글",
                body="이 글은 user1이 작성한 공개 글입니다.",
                url="#",
                image_path="",
                is_public=True,
                cat="study",
                cat_detail="python"
            ),
            Post(
                author_id=user1.id,
                title="user1 비공개 글",
                body="이 글은 user1이 작성한 비공개 글입니다.",
                url="#",
                image_path="",
                is_public=False,
                cat="tip",
                cat_detail="docker"
            ),
            Post(
                author_id=user2.id,
                title="user2 공개 글",
                body="이 글은 user2가 작성한 공개 글입니다.",
                url="#",
                image_path="",
                is_public=True,
                cat="post",
                cat_detail="git"
            ),
        ]

        db.add_all(posts)
        db.commit()

        # url 후처리
        for p in db.query(Post).all():
            p.url = f"/post/{p.id}"
        db.commit()

    finally:
        db.close()     



####################################################################################


app= FastAPI()

app.add_middleware(SessionMiddleware, secret_key="Change_me_SECRET_KEY")

Base.metadata.create_all(bind= engine)
## Test
send_test_data()

AVATAR_DIR= Path("data/uploads/avatars")
AVATAR_DIR.mkdir(parents= True, exist_ok= True)
POST_IMAGE_DIR= Path("data/uploads/posts")
POST_IMAGE_DIR.mkdir(parents= True, exist_ok= True)
PROJECT_IMAGE_DIR= Path("data/uploads/projects")
PROJECT_IMAGE_DIR.mkdir(parents= True, exist_ok= True)

app.mount("/static", StaticFiles(directory= "app/static"), name= "static")
app.mount("/uploads/avatars", StaticFiles(directory= "data/uploads/avatars"), name= "avatars")
app.mount("/uploads", StaticFiles(directory= "data/uploads"), name= "uploads")


templates= Jinja2Templates(directory="app/templates")

####################################################################################

POST_TYPES = [
    {"value": "notice", "label": "NOTICE"},
    {"value": "study", "label": "STUDY"},
    {"value": "tip", "label": "TIP"},
    {"value": "post", "label": "POST"},
    {"value": "review", "label": "리뷰"}
]
POST_DETAILS = [
    {"value": "aws", "label": "AWS"},
    {"value": "docker", "label": "Docker"},
    {"value": "git", "label": "Git"},
    {"value": "devops", "label": "DevOps"},
    {"value": "ci/cd", "label": "CI/CD"},
    {"value": "iac", "label": "IaC"},
    {"value": "python", "label": "Python"},
    {"value": "life", "label": "LIFE"},
    {"value": "daily", "label": "Daily"},
    {"value": "event", "label": "Event"},
    {"value": "etc", "label": "기타"}
]

###### URL ##############################################################################

###### PAGE ##############################################################################


@app.get("/")
def home(request:Request):
    current_user= request.session.get("user")

    db= SessionLocal()
    try:
        if not current_user:
            posts_db= (
                db.query(Post)
                .filter(Post.is_public == True)
                .order_by(Post.created_at.desc())
                .all()
            )
        elif current_user["role"] == "mgr":
            posts_db= (
                db.query(Post)
                .order_by(Post.created_at.desc())
                .all()
            )
        else:
            posts_db= (
                db.query(Post)
                .filter(
                    or_(
                        Post.is_public == True,
                        Post.author_id == current_user["id"]
                    )
                )
                .order_by(Post.created_at.desc())
                .all()
            )

        posts= []
        all_posts= []
        for p in posts_db:
            posts.append({
                "cat": p.cat,
                "catLabel": p.cat_detail,
                "title": p.title,
                "body": (p.body[:120] + "...") if p.body and len(p.body) > 120 else (p.body or ""),
                "date": p.created_at.strftime("%Y.%m.%d"),
                "url": f"/post/{p.id}"
            })

            all_posts.append({
                "date": p.created_at.strftime("%Y.%m.%d"),
                "title": p.title,
                "tag": p.cat_detail,
                "url": f"/post/{p.id}"
            })

        projects_db= (
            db.query(Project)
            .filter(Project.is_public == True)
            .order_by(Project.created_at.desc())
            .all()
        )

        project_count= len(projects_db)

        projects= []
        for prj in projects_db:
            status_label_map = {
                "planning": "● planning",
                "in_progress": "● progress",
                "testing": "● testing",
                "done": "● done",
            }            

            projects.append({
                "emoji": "🚀",
                "bg": "#0D1E35",
                "name": prj.name,
                "tags": [t.strip() for t in prj.stack.split(",") if t.strip()] if prj.stack else [],
                "platforms": [prj.status],
                "url": f"/project/{prj.id}"
            })



        return templates.TemplateResponse(
            request= request,
            name= "index.html",
            context= {
                "posts": posts,
                "all_posts": all_posts,
                "projects": projects,
                "current_user": current_user,
                "project_count": project_count
            }
        )
    finally:
            db.close()

@app.get("/dashboard")
def dashboard(request:Request):
    current_user= request.session.get("user")

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    if current_user.get("role") != "mgr":
        return HTMLResponse("Forbidden", status_code= 403)

    db= SessionLocal()
    try:
        recent_posts_db= (
            db.query(Post)
            .order_by(Post.updated_at.desc())
            .limit(3)
            .all()
        )

        recent_posts= []
        for p in recent_posts_db:
            recent_posts.append({
                "id": p.id,
                "title": p.title,
                "cat": p.cat_detail,
                "date": p.updated_at.strftime("%Y.%m.%d"),
                "public": p.is_public
            })
        
        recent_project_db= (
            db.query(Project)
            .order_by(Project.updated_at.desc())
            .first()
        )

        recent_project= None
        if recent_project_db:
            recent_project= {
                "id": recent_project_db.id,
                "name": recent_project_db.name,
                "status": recent_project_db.status,
                "date": recent_project_db.updated_at.strftime("%Y.%m.%d"),
                "public": recent_project_db.is_public
            }

        status_panel = [
            {"label": "Server", "value": "Running", "state": "ok"},
            {"label": "Environment", "value": "Local", "state":"warn"},
            {"label": "Docker", "value": "Enabled", "state": "ok"},
            {"label": "DB", "value": "Connected", "state": "ok"},
            {"label": "Version", "value": "v0.1.0", "state": "info"},
            {"label": "Mode", "value": "Manager", "state": "accent"},
        ]

        return templates.TemplateResponse(
            request= request,
            name= "dashboard.html",
            context={
                "current_user": current_user,
                "recent_posts": recent_posts,
                "recent_project": recent_project,
                "status_panel": status_panel
            }
        )
    finally:
        db.close()


##### LOGIN ###############################################################################

@app.get("/login")
def login_page(request:Request):
    return templates.TemplateResponse(
        request= request,
        name= "login.html",
        context={
            "form": {"username": "", "password": ""}
        }
    )

@app.post("/login")
def login_submit(request:Request, username: str = Form(...), password: str = Form(...)):
    db= SessionLocal()

    try:
        user= db.query(User).filter(User.username == username).first()
        if not user or user.password != password:
            return templates.TemplateResponse(
                request= request,
                name= "login.html",
                context={
                    "form": {"username": username, "password": password},
                    "message": "아이디 또는 비밀번호가 일치하지 않습니다.",
                    "message_type": "error"
                }
            )
        request.session["user"]= {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "avatar_image": user.avatar_image,
            "role": user.role
        }
        return RedirectResponse(url="/", status_code=303)
    finally:
        db.close()

@app.get("/logout")
def logout(request:Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@app.get("/signup")
def signup_page(request:Request):
    return templates.TemplateResponse(
        request= request,
        name= "signup.html",
        context={
            "form": {"username_display": "", "username": ""}
        }
    )

@app.post("/signup")
def signup_submit(
    request:Request,
    username: str = Form(...),
    password: str = Form(...),
    username_display: str = Form(...),
    profile_image: UploadFile | None = File(None)
    ):
    db= SessionLocal()
    try:
        existing_user= db.query(User).filter(User.username == username).first()
        if existing_user:
            return templates.TemplateResponse(
                request= request,
                name= "signup.html",
                context={
                    "form": {"username": username, "username_display": username_display},
                    "message": "이미 존재하는 아이디입니다.",
                    "message_type": "error"
                }
            )
        
        avatar_path= None
        if profile_image and profile_image.filename:
            unique_name= f"{uuid4()}_{profile_image.filename}"
            save_path= AVATAR_DIR / unique_name
            with open(save_path, "wb") as f:
                f.write(profile_image.file.read())
            avatar_path= f"/uploads/avatars/{unique_name}"

        new_user= User(
            username= username,
            nickname= username_display,
            password= password,
            avatar_image= avatar_path
        )
        db.add(new_user)
        db.commit()
        return RedirectResponse(url="/login", status_code=303)
    finally:
        db.close()


############# CRUD Operations for Posts ####################################################

@app.get("/post/new")
def post_new_page(request:Request):
    current_user= request.session.get("user")

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request= request,
        name= "post_form.html",
        context={
            "current_user": current_user,
            "post": None,
            "post_types": POST_TYPES,
            "post_details": POST_DETAILS
        }
    )

@app.post("/post/new")
def post_create(
    request: Request,
    title: str = Form(...),
    cat: str = Form(...),
    cat_detail: str = Form(...),
    body: str = Form(...),
    is_public: str | None = Form(None),
    thumbnail: UploadFile | None = File(None)
):
    current_user = request.session.get("user")

    if not current_user:
        return RedirectResponse(url= "/login", status_code=303)

    db = SessionLocal()

    try:
        db_user= db.query(User).filter(User.id == current_user["id"]).first()

        if not db_user:
            return RedirectResponse(url= "/login", status_code= 303)

        image_path = ""

        if thumbnail and thumbnail.filename:
            unique_name = f"{uuid4()}_{thumbnail.filename}"
            filepath = POST_IMAGE_DIR / unique_name

            with open(filepath, "wb") as f:
                f.write(thumbnail.file.read())

            image_path = f"/uploads/posts/{unique_name}"

        new_post = Post(
            title= title,
            body= body,
            cat= cat,
            cat_detail= cat_detail,
            url= "#",
            image_path= image_path,
            is_public= True if is_public else False,
            author_id= db_user.id
        )

        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        new_post.url = f"/post/{new_post.id}"
        db.commit()

        return RedirectResponse(f"/post/{new_post.id}", status_code=303)

    finally:
        db.close()


@app.get("/post/{post_id}")
def post_detail(request: Request, post_id: int):
    current_user= request.session.get("user")

    db= SessionLocal()
    try:
        p= db.query(Post).filter(Post.id == post_id).first()

        if not p:
            return HTMLResponse("Post not found", status_code= 404)

        author= db.query(User).filter(User.id == p.author_id).first()

        post_view= {
            "id": p.id,
            "title": p.title,
            "category": f"{p.cat} / {p.cat_detail}",
            "thumbnail": p.image_path if p.image_path else None,
            "created_at": p.created_at.strftime("%Y.%m.%d %H:%M"),
            "content_html": (p.body or "").replace("\n", "<br>"),
            "author_name": author.nickname if author else "Unknown",
            "author_initials": (author.nickname[:2].upper() if author and author.nickname else "UN"),
            "author_bio": "DevLog 사용자",
            "read_time": max(1, len((p.body or "").split()) // 200),
            "tags": [p.cat_detail] if p.cat_detail else []
            }

        is_owner= bool(current_user and can_edit_or_delete(current_user, p))

        return templates.TemplateResponse(
            request= request,
            name= "post_detail.html",
            context= {
                "post": post_view,
                "current_user": current_user,
                "is_owner": is_owner,
                "prev_post": None,
                "next_post": None
            }
        )
    finally:
        db.close()

@app.get("/post/{post_id}/edit")
def post_edit_page(request: Request, post_id: int):
    current_user= request.session.get("user")

    if not current_user:
        return RedirectResponse(url= "/login", status_code= 303)
    
    db= SessionLocal()
    try:
        post= db.query(Post).filter(Post.id == post_id).first()

        if not post:
            return HTMLResponse("Post not found", status_code= 404)
        
        if not can_edit_or_delete(current_user, post):
            return HTMLResponse("Forbidden", status_code= 403)
        
        return templates.TemplateResponse(
            request= request,
            name= "post_form.html",
            context= {
                "current_user": current_user,
                "post": post,
                "post_types": POST_TYPES,
                "post_details": POST_DETAILS
            }
        )
    finally:
        db.close()

@app.post("/post/{post_id}/edit")
def post_edit_submit(
    request: Request,
    post_id: int,
    title: str= Form(...),
    cat: str = Form(...),
    cat_detail: str = Form(...),
    body: str = Form(...),
    is_public: str | None = Form(None),
    thumbnail: UploadFile | None = File(None)
):
    current_user= request.session.get("user")

    if not current_user:
        return RedirectResponse(url= "/login", status_code= 303)

    db= SessionLocal()
    try:
        post= db.query(Post).filter(Post.id == post_id).first()

        if not post:
            return HTMLResponse("Post not found", status= 404)
        
        if not can_edit_or_delete(current_user, post):
            return HTMLResponse("Forbidden", status_code= 403)

        post.title= title
        post.cat= cat
        post.cat_detail= cat_detail
        post.body= body
        post.is_public= True if is_public else False
        
        if thumbnail and thumbnail.filename:
            unique_name= f"{uuid4()}_{thumbnail.filename}"
            save_path= POST_IMAGE_DIR / unique_name

            with open(save_path, "wb") as f:
                f.write(thumbnail.file.read())

            post.image_path= f"/uploads/posts/{unique_name}"

        db.commit()

        return RedirectResponse(url= f"/post/{post_id}", status_code= 303)

    finally:
        db.close()


@app.post("/post/{post_id}/delete")
def post_delete(request: Request, post_id: int):
    current_user= request.session.get("user")

    if not current_user:
        return RedirectResponse(url= "/login", status_code= 303)

    db= SessionLocal()
    try:
        post= db.query(Post).filter(Post.id == post_id).first()

        if not post:
            return HTMLResponse("Post not found", status_code= 404)

        if not can_edit_or_delete(current_user, post):
            return HTMLResponse("Forbidden", status_code= 403)

        db.delete(post)
        db.commit()

        return RedirectResponse(url= "/", status_code= 303)

    finally:
        db.close()

############# CRUD Operations for Projects ####################################################


@app.get("/project/new")
def project_new_page(request: Request):
    current_user= request.session.get("user")

    if not current_user:
        return RedirectResponse(url= "/login", status_code= 303)
    
    if current_user.get("role") != "mgr":
        return HTMLResponse("Forbidden", status_code= 403)

    return templates.TemplateResponse(
        request= request,
        name= "project_form.html",
        context= {
            "current_user" : current_user,
            "project" : None
        }
    )

@app.post("/project/new")
def project_create(
    request: Request,
    name: str = Form(...),
    summary: str = Form(...),
    description: str = Form(...),
    stack: str = Form(""),
    status: str = Form(...),
    demo_url: str = Form(""),
    github_url: str = Form(""),
    is_public: str | None = Form(None),
    thumbnail: UploadFile | None = File(None)
):
    current_user= request.session.get("user")

    if not current_user:
        return RedirectResponse(url= "/login", status_code= 303)

    if current_user.get("role") != "mgr":
        return HTMLResponse("Forbidden", status_code=403)

    db= SessionLocal()
    try:
        image_path= ""

        if thumbnail and thumbnail.filename:
            unique_name = f"{uuid4()}_{thumbnail.filename}"
            save_path = PROJECT_IMAGE_DIR / unique_name

            with open(save_path, "wb") as buffer:
                buffer.write(thumbnail.file.read())

            image_path = f"/uploads/projects/{unique_name}"

        new_project = Project(
            name=name,
            summary=summary,
            description=description,
            image_path=image_path,
            stack=stack,
            status=status,
            demo_url=demo_url if demo_url else None,
            github_url=github_url if github_url else None,
            is_public=True if is_public else False
        )

        db.add(new_project)
        db.commit()
        
        return RedirectResponse(url= "/", status_code= 303)

    finally:
        db.close()

@app.get("/project/{project_id}")
def project_detail(request: Request, project_id: int):
    current_user = request.session.get("user")

    db = SessionLocal()
    try:
        p = db.query(Project).filter(Project.id == project_id).first()

        if not p:
            return HTMLResponse("Project not found", status_code=404)

        project_view = {
            "id": p.id,
            "name": p.name,
            "summary": p.summary,
            "description": p.description,
            "thumbnail": p.image_path if p.image_path else None,
            "stack": [t.strip() for t in p.stack.split(",") if t.strip()] if p.stack else [],
            "status": p.status,
            "demo_url": p.demo_url,
            "github_url": p.github_url,
            "is_public": p.is_public,
            "created_at": p.created_at.strftime("%Y.%m.%d %H:%M"),
        }

        is_owner = bool(current_user and current_user.get("role") == "mgr")

        return templates.TemplateResponse(
            request=request,
            name="project_detail.html",
            context={
                "project": project_view,
                "current_user": current_user,
                "is_owner": is_owner
            }
        )

    finally:
        db.close()

@app.get("/project/{project_id}/edit")
def project_edit_page(request: Request, project_id: int):
    current_user = request.session.get("user")

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    if current_user.get("role") != "mgr":
        return HTMLResponse("Forbidden", status_code=403)

    db = SessionLocal()
    try:
        p = db.query(Project).filter(Project.id == project_id).first()

        if not p:
            return HTMLResponse("Project not found", status_code=404)

        project_view = {
            "id": p.id,
            "name": p.name,
            "summary": p.summary,
            "description": p.description,
            "thumbnail": p.image_path if p.image_path else None,
            "stack": p.stack,
            "status": p.status,
            "demo_url": p.demo_url or "",
            "github_url": p.github_url or "",
            "is_public": p.is_public
        }

        return templates.TemplateResponse(
            request=request,
            name="project_form.html",
            context={
                "current_user": current_user,
                "project": project_view
            }
        )

    finally:
        db.close()

@app.post("/project/{project_id}/edit")
def project_edit_submit(
    request: Request,
    project_id: int,
    name: str = Form(...),
    summary: str = Form(...),
    description: str = Form(...),
    stack: str = Form(""),
    status: str = Form(...),
    demo_url: str = Form(""),
    github_url: str = Form(""),
    is_public: str | None = Form(None),
    thumbnail: UploadFile | None = File(None)
):
    current_user = request.session.get("user")

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    if current_user.get("role") != "mgr":
        return HTMLResponse("Forbidden", status_code=403)

    db = SessionLocal()
    try:
        p = db.query(Project).filter(Project.id == project_id).first()

        if not p:
            return HTMLResponse("Project not found", status_code=404)

        p.name = name
        p.summary = summary
        p.description = description
        p.stack = stack
        p.status = status
        p.demo_url = demo_url if demo_url else None
        p.github_url = github_url if github_url else None
        p.is_public = True if is_public else False

        if thumbnail and thumbnail.filename:
            unique_name = f"{uuid4()}_{thumbnail.filename}"
            save_path = PROJECT_IMAGE_DIR / unique_name

            with open(save_path, "wb") as buffer:
                buffer.write(thumbnail.file.read())

            p.image_path = f"/uploads/projects/{unique_name}"

        db.commit()

        return RedirectResponse(url=f"/project/{p.id}", status_code=303)

    finally:
        db.close()

@app.post("/project/{project_id}/delete")
def project_delete(request: Request, project_id: int):
    current_user = request.session.get("user")

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    if current_user.get("role") != "mgr":
        return HTMLResponse("Forbidden", status_code=403)

    db = SessionLocal()
    try:
        p = db.query(Project).filter(Project.id == project_id).first()

        if not p:
            return HTMLResponse("Project not found", status_code=404)

        db.delete(p)
        db.commit()

        return RedirectResponse(url="/", status_code=303)

    finally:
        db.close()