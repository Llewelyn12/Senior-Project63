from flask import Flask, render_template, jsonify
import cv2
from ultralytics import YOLO

app = Flask(__name__)

VIDEO_PATH_1 = "static/video/sampletest1.mp4"
VIDEO_PATH_2 = "static/video/sampletest2.mp4"
MODEL_PATH = "static/model/table-detection.pt"

video = cv2.VideoCapture(VIDEO_PATH_1)
video2 = cv2.VideoCapture(VIDEO_PATH_2)
model = YOLO(MODEL_PATH)


def process_video(video, model):
    ret, frame = video.read()
    new_width, new_height = 1000, 600
    frame = cv2.resize(frame, (new_width, new_height))
    result = model(frame, verbose=True, device=0)
    return result

def analyze_table_status(result, persons, tables, objects):
    for r in result:
        boxes = r.boxes
        for box in boxes:
            b = box.xyxy[0]
            x = int(b[0])
            y = int(b[1])
            x1 = int(b[2])
            y1 = int(b[3])
            cls = int(box.cls)
            
            if model.names[box.cls.item()] == 'person':
                persons.append(((x, y), (x1, y1)))
            elif model.names[box.cls.item()] == 'table':
                tables.append(((x, y), (x1, y1)))
            elif model.names[box.cls.item()] == 'object':
                objects.append(((x, y), (x1, y1)))

def analyze_table_statuses(tables, persons, objects):
    table_statuses = {}
    
    for i, ((x_table, y_table), (x1_table, y1_table)) in enumerate(tables):
            num_people_at_table = 0

            for (x_person, y_person), (x1_person, y1_person) in persons:
                overlap_area = max(0, min(x1_table, x1_person) - max(x_table, x_person)) * max(0, min(y1_table, y1_person) - max(y_table, y_person))
                area_person = (x1_person - x_person) * (y1_person - y_person)

                if overlap_area / area_person >= 0.35:
                    num_people_at_table += 1

            is_table_reserved = any(
                x_object < x1_table and x1_object > x_table and y_object < y1_table and y1_object > y_table
                and (max(0, min(x1_table, x1_object) - max(x_table, x_object)) * max(0, min(y1_table, y1_object) 
                - max(y_table, y_object))) / ((x1_object - x_object) * (y1_object - y_object)) >= 0.85
                for (x_object, y_object), (x1_object, y1_object) in objects
            )

            if num_people_at_table <= 2 and not is_table_reserved:
                table_statuses[(x_table, y_table)] = "empty"

            elif num_people_at_table >= 1 and is_table_reserved:
                table_statuses[(x_table, y_table)] = "occupied"

            elif num_people_at_table > 2:
                table_statuses[(x_table, y_table)] = "occupied"

            else:
                table_statuses[(x_table, y_table)] = "reserved"
        
    tables = sorted(tables, key=lambda table: table[0][0])

    for i, ((x_table, y_table), (x1_table, y1_table)) in enumerate(tables):
        print(f"Table {i + 1}, Status: {table_statuses[(x_table, y_table)]}")
    
    return table_statuses

def calculate_percentages_and_message(table_statuses, total_tables):
    empty_tables = sum(1 for status in table_statuses.values() if status == "empty")
    occupied_tables = sum(1 for status in table_statuses.values() if status == "occupied")
    reserved_tables = sum(1 for status in table_statuses.values() if status == "reserved")

    total_tables_both_images = total_tables + len(table_statuses)
    empty_tables_both_images = empty_tables + sum(1 for status in table_statuses.values() if status == "empty")
    occupied_tables_both_images = occupied_tables + sum(1 for status in table_statuses.values() if status == "occupied")
    reserved_tables_both_images = reserved_tables + sum(1 for status in table_statuses.values() if status == "reserved")

    percentages_both_images = {
        "empty": round((empty_tables_both_images / total_tables_both_images) * 100, 2),
        "occupied": round((occupied_tables_both_images / total_tables_both_images) * 100, 2),
        "reserved": round((reserved_tables_both_images / total_tables_both_images) * 100, 2)
    }

    if percentages_both_images["empty"] >= 35:
        message_both_images = "There is ample space. You are welcome to come in now."
    elif percentages_both_images["occupied"] >= 70:
        message_both_images = "Please relocate as there is limited space available."
    else:
        message_both_images = "The space is available."

    return percentages_both_images, message_both_images

@app.route('/')
def index():
    return render_template('home.html', video_path=VIDEO_PATH_1, video_path2=VIDEO_PATH_2)

@app.route('/update_table_status')
def update_table_status():
    result = process_video(video, model)

    persons = []
    tables = []
    objects = []
    analyze_table_status(result, persons, tables, objects)

    table_statuses = analyze_table_statuses(tables, persons, objects)
    
    result2 = process_video(video2, model)

    persons2 = []
    tables2 = []
    objects2 = []
    analyze_table_status(result2, persons2, tables2, objects2)

    table_statuses2 = analyze_table_statuses(tables2, persons2, objects2)

    combined_table_statuses = {**table_statuses, **table_statuses2}

    total_tables = len(table_statuses) + len(table_statuses2)
    
    percentages_both_images, message_both_images = calculate_percentages_and_message(combined_table_statuses, total_tables)
    
    sorted_statuses = dict(sorted(table_statuses.items(), key=lambda x: x[0]))
    sorted_statuses2 = dict(sorted(table_statuses2.items(), key=lambda x: x[0]))

    return jsonify({
        'table_status_array': list(sorted_statuses.values()),
        'table_status_array2': list(sorted_statuses2.values()),
        'percentages': percentages_both_images,
        'message': message_both_images
    })

if __name__ == '__main__':
    app.run(debug=True)
 