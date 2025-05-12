import json
import os

# Create the uploads directory if it doesn't exist
os.makedirs('static/uploads', exist_ok=True)

# Sample worker data
workers = [
    {
        "name": "Rajesh Kumar",
        "skill": "Electrician",
        "description": "Experienced electrician with over 5 years of work in residential and commercial buildings. Specializing in wiring, circuit repairs, and installations.",
        "location": "Delhi",
        "experience": "5",
        "contact": "919876543210",
        "image": "/static/uploads/electrician.jpg"
    },
    {
        "name": "Mohan Singh",
        "skill": "Plumbing",
        "description": "Professional plumber offering services for pipe installation, leak repairs, bathroom fixtures, and drainage systems. Quality work guaranteed.",
        "location": "Mumbai",
        "experience": "7",
        "contact": "918765432109",
        "image": "/static/uploads/plumbing.jpg"
    },
    {
        "name": "Anil Sharma",
        "skill": "Painting",
        "description": "Skilled painter providing interior and exterior painting services. Specializing in wall textures, decorative finishes, and color consultation.",
        "location": "Bangalore",
        "experience": "3",
        "contact": "917654321098",
        "image": "/static/uploads/painting.jpg"
    },
    {
        "name": "Suresh Patel",
        "skill": "Flooring",
        "description": "Flooring expert with experience in tile, hardwood, laminate, and vinyl installation. Provides quality workmanship and timely completion.",
        "location": "Ahmedabad",
        "experience": "8",
        "contact": "916543210987",
        "image": "/static/uploads/flooring.jpg"
    },
    {
        "name": "Kavita Reddy",
        "skill": "Cleaning",
        "description": "Professional home and office cleaning services. Thorough deep cleaning, sanitization, and organization services available on regular or one-time basis.",
        "location": "Hyderabad",
        "experience": "4",
        "contact": "915432109876",
        "image": "/static/uploads/cleaning.jpg"
    }
]

# Save the worker data to workers.json
with open('workers.json', 'w') as f:
    json.dump(workers, f, indent=4)

print(f"Created sample data for {len(workers)} workers")

# Create placeholder images if they don't exist
placeholder_images = {
    "electrician.jpg": "blue",
    "plumbing.jpg": "red",
    "painting.jpg": "green",
    "flooring.jpg": "orange",
    "cleaning.jpg": "purple"
}

for image_name, color in placeholder_images.items():
    image_path = os.path.join('static/uploads', image_name)
    
    # Only create the image if it doesn't exist
    if not os.path.exists(image_path):
        # Create a simple colored SVG image
        svg_content = f'''
        <svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="{color}"/>
            <text x="50%" y="50%" font-family="Arial" font-size="50" fill="white" text-anchor="middle">
                {image_name.split('.')[0].title()}
            </text>
        </svg>
        '''
        
        with open(image_path, 'w') as img_file:
            img_file.write(svg_content)
        
        print(f"Created placeholder image: {image_path}")
        
print("Sample data and images created successfully!")