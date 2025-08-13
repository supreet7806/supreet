# app.py
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)
sessions = []        # Stores all conference sessions
my_schedule = []     # Stores sessions selected by the attendee

# HTML templates with attractive styling
home_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Conference Session Planner</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 20px; }
        .session-item { background: #f9f9f9; margin-bottom: 10px; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }
        .session-item h3 { margin: 0 0 5px 0; color: #2c3e50; }
        .session-meta { color: #7f8c8d; font-size: 0.9em; margin-bottom: 10px; }
        .btn { display: inline-block; background: #3498db; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; margin-right: 10px; }
        .btn:hover { background: #2980b9; }
        .nav { margin: 20px 0; text-align: center; }
        .error { background: #ffdddd; padding: 10px; border-radius: 4px; margin: 10px 0; color: #d63031; }
    </style>
</head>
<body>
<div class="container">
    <h1>Conference Sessions</h1>
    
    <div class="nav">
        <a href="/admin" class="btn">Add Session (Admin)</a>
        <a href="/mine" class="btn">View My Schedule</a>
    </div>
    
    {% if sessions %}
        {% for s in sessions %}
        <div class="session-item">
            <h3>{{ s['topic'] }}</h3>
            <div class="session-meta">
                Speaker: {{ s['speaker'] }} | Time: {{ s['start'] }} - {{ s['end'] }}
            </div>
            <a href="/add_to_schedule/{{ loop.index0 }}" class="btn">Add to My Schedule</a>
        </div>
        {% endfor %}
    {% else %}
        <p>No sessions available yet. Admin can add sessions.</p>
    {% endif %}
</div>
</body>
</html>
"""

admin_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Add Session - Conference Planner</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 600px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { background: #3498db; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .back-link { display: inline-block; margin-top: 15px; color: #3498db; text-decoration: none; }
    </style>
</head>
<body>
<div class="container">
    <h1>Add New Session</h1>
    
    <form method="post">
        <div class="form-group">
            <label for="speaker">Speaker:</label>
            <input type="text" id="speaker" name="speaker" required>
        </div>
        
        <div class="form-group">
            <label for="topic">Topic:</label>
            <input type="text" id="topic" name="topic" required>
        </div>
        
        <div class="form-group">
            <label for="start">Start Time (HH:MM):</label>
            <input type="text" id="start" name="start" placeholder="09:00" required>
        </div>
        
        <div class="form-group">
            <label for="end">End Time (HH:MM):</label>
            <input type="text" id="end" name="end" placeholder="10:30" required>
        </div>
        
        <button type="submit" class="btn">Add Session</button>
    </form>
    
    <a href="/" class="back-link">← Back to Sessions</a>
</div>
</body>
</html>
"""

mine_html = """
<!DOCTYPE html>
<html>
<head>
    <title>My Schedule - Conference Planner</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4; }
        .container { max-width: 800px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 20px; }
        .schedule-item { background: #f9f9f9; margin-bottom: 10px; padding: 15px; border-radius: 5px; border-left: 4px solid #2ecc71; }
        .schedule-item h3 { margin: 0 0 5px 0; color: #2c3e50; }
        .schedule-meta { color: #7f8c8d; font-size: 0.9em; margin-bottom: 5px; }
        .empty-schedule { text-align: center; padding: 30px; color: #7f8c8d; }
        .back-link { display: inline-block; margin-top: 15px; color: #3498db; text-decoration: none; }
    </style>
</head>
<body>
<div class="container">
    <h1>My Schedule</h1>
    
    {% if my_schedule %}
        {% for s in my_schedule %}
        <div class="schedule-item">
            <h3>{{ s['topic'] }}</h3>
            <div class="schedule-meta">
                Speaker: {{ s['speaker'] }} | Time: {{ s['start'] }} - {{ s['end'] }}
            </div>
        </div>
        {% endfor %}
    {% else %}
        <div class="empty-schedule">
            <p>Your schedule is empty.</p>
            <p>Add sessions from the main page to build your schedule.</p>
        </div>
    {% endif %}
    
    <a href="/" class="back-link">← Back to All Sessions</a>
</div>
</body>
</html>
"""

def time_to_minutes(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

@app.route('/')
def home():
    return render_template_string(home_html, sessions=sessions)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        sessions.append({
            'speaker': request.form['speaker'],
            'topic': request.form['topic'],
            'start': request.form['start'],
            'end': request.form['end']
        })
        return redirect('/')
    return render_template_string(admin_html)

@app.route('/add_to_schedule/<int:idx>')
def add_to_schedule(idx):
    session = sessions[idx]
    new_start = time_to_minutes(session['start'])
    new_end = time_to_minutes(session['end'])
    for s in my_schedule:
        if not (new_end <= time_to_minutes(s['start']) or new_start >= time_to_minutes(s['end'])):
            return f"""
            <div style="max-width: 600px; margin: 50px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); text-align: center;">
                <h2 style="color: #e74c3c;">Schedule Conflict</h2>
                <p>Cannot add <strong>'{session['topic']}'</strong> because it overlaps with:</p>
                <div style="background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <strong>{s['topic']}</strong><br>
                    {s['start']} - {s['end']}
                </div>
                <a href="/" style="display: inline-block; background: #3498db; color: white; padding: 10px 15px; border-radius: 4px; text-decoration: none;">Back to Sessions</a>
            </div>
            """
    my_schedule.append(session)
    return redirect('/mine')

@app.route('/mine')
def mine():
    return render_template_string(mine_html, my_schedule=my_schedule)

if __name__ == '__main__':
    app.run(debug=True)