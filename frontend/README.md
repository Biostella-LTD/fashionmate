Fashion Mate

Your AI-powered fashion assistant! Fashion Mate helps you manage your wardrobe, analyze your personal style, and generate stunning outfit recommendations—effortlessly.

✨ Features

👤 Profile

Upload and analyze face and body images

Get personalized feature analysis

AI-powered detection of facial features, body shape, and proportions

👗 Wardrobe

Upload and manage your clothing items

Automatic categorization (tops, bottoms, dresses, etc.)

View detailed clothing insights

Interactive item cards with flip animations

🎨 Outfit Generation

Select from various occasions (casual, work, formal, etc.)

AI-powered outfit recommendations tailored to your wardrobe

Complete ensembles with tops, bottoms, outerwear, footwear, and accessories

Regenerate outfits until you find your perfect look

🏗 Architecture

Frontend (Flutter)

🔐 Authentication: Secure login & registration

👤 Profile Management: Upload & analyze personal features

👕 Wardrobe Management: Upload, view, and delete clothing items

🎭 Outfit Selection: Choose occasions & view AI-generated outfits

Backend (Azure Functions)

🔑 User Authentication: JWT-based security

📸 Image Processing: Upload & store images securely

🔍 Feature Analysis: AI-driven personal style insights

👗 Wardrobe Management: Store and retrieve fashion items

🤖 Outfit Generation: AI-powered recommendations

Storage

🛢 MongoDB: User data, wardrobe items, and analysis results

☁ Azure Blob Storage: Secure storage for user images

🔧 Technical Implementation

📱 Flutter App

State Management: Singleton services for efficient caching

Networking: Secure API calls to Azure Functions backend

Image Handling: Cached network images for performance

UI Components: Custom interactive widgets

☁ Azure Functions

API Endpoints: RESTful APIs for all features

Authentication: JWT token verification for security

Blob Storage: Secure image handling with SAS tokens

MongoDB Integration: Persistent wardrobe and user data

AI Services: External API calls for analysis & outfit generation

🚀 Getting Started

Prerequisites

Flutter 3.0+

Dart 2.17+

Azure account (for backend deployment)

MongoDB database

Setup

Clone the repository:

git clone https://github.com/your-repo/fashion-mate.git

Navigate to the project directory:

cd fashion-mate

Install dependencies:

flutter pub get

Configure Azure Function URLs in the services

Run the app:

flutter run

📦 Building for Production

Android:

flutter build apk --release

iOS:

flutter build ios --release

🛠 Backend Configuration

Fashion Mate relies on multiple Azure Function endpoints:

/register - User registration

/login - User authentication

/uploadImage - Upload profile images

/getSasToken - Secure access to stored images

/uploadWardrobe - Upload clothing items

/getWardrobe - Retrieve wardrobe items

/deleteWardrobe - Remove wardrobe items

/generateOutfit - Get AI-powered outfit recommendations

🔮 Future Enhancements

📅 Outfit history

❤️ Favorite outfits

📲 Social sharing

🌦 Seasonal outfit recommendations

🎉 Get ready to redefine your style with Fashion Mate! 👗👔👠

