from server import db

class TrackingAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.TIMESTAMP(), unique=True)
    all_user_count = db.Column(db.Integer)
    active_user_count = db.Column(db.Integer)
    new_user_count = db.Column(db.Integer)
    return_user_count = db.Column(db.Integer)
    view_count = db.Column(db.Integer)
    view_item_count = db.Column(db.Integer)
    add_to_cart_count = db.Column(db.Integer)
    checkout_count = db.Column(db.Integer)

class TrackingRaw(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_url = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.TIMESTAMP())

class TrackingRealtime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(127), nullable=False)
    time = db.Column(db.TIMESTAMP(), nullable=False)
    event_type = db.Column(db.String(255), nullable=False)
    view_detail = db.Column(db.String(255))
    item_id = db.Column(db.Integer)
    checkout_step = db.Column(db.Integer)

class TrackingUserEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    system = db.Column(db.String(127), nullable=False)
    version = db.Column(db.String(127), nullable=False)
    event = db.Column(db.String(255), nullable=False)
    event_detail = db.Column(db.String(255), nullable=False)
    user_email = db.Column(db.String(255))
    device_id = db.Column(db.String(255), nullable=False)
    created_time = db.Column(db.TIMESTAMP(), nullable=False)

def get_user_behavior_by_date(date):
    analysis = TrackingAnalysis.query.filter_by(date = date + ' 00:00:00').all()
    if analysis:
        return analysis[0].to_json()
    else:
        return None

def create_user_event(event):
    try:
        event_model = TrackingUserEvent(**event)
        db.session.add(event_model)
        db.session.flush()
        db.session.commit()
    except Exception as e:
        print(e)