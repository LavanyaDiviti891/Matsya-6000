# Matsya-6000

A full-stack web application combining FastHTML backend with React + Vite frontend.

## Overview

Matsya-6000 is a modern web application featuring:
- **Backend**: FastHTML-powered API
- **Frontend**: React with Vite for optimal build performance
- **Deployment**: Docker-ready containerization

## Tech Stack

### Backend
- **FastHTML**: Lightweight Python web framework
- **Python**: Core language for backend logic

### Frontend
- **React**: Modern UI library
- **Vite**: Next-generation frontend tooling
- **TypeScript**: Type-safe development
- **Oxlint**: Fast JavaScript linter

## Project Structure

```
Matsya-6000/
├── README.md                 # Main project documentation
├── frontend/                 # React + Vite application
│   ├── README.md
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   └── public/
├── requirements.txt          # Python dependencies
└── app.py                    # FastHTML application
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Docker (optional, for containerized deployment)

### Installation

#### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

#### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

### Running the Application

#### Development Mode

**Backend**:
```bash
python app.py
```

**Frontend** (in another terminal):
```bash
cd frontend
npm run dev
```

#### Production Build

**Frontend**:
```bash
cd frontend
npm run build
```

### Docker Deployment

Build and run the application in a Docker container:

```bash
docker build -t matsya-6000 .
docker run -p 7860:7860 matsya-6000
```

The application will be available at `http://localhost:7860`

## Configuration

### Frontend
- **App Port**: 7860
- **SDK**: Docker
- **Framework**: React + Vite

### Development Tools
- **Linter**: Oxlint for fast code quality checks
- **HMR**: Hot Module Replacement enabled for rapid development

## Features

- ⚡ Lightning-fast frontend with Vite
- 🔥 Hot Module Replacement (HMR) for seamless development
- 🐍 Lightweight Python backend with FastHTML
- 🐳 Docker-ready for easy deployment
- 📦 Optimized build system

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## Development Workflow

### Frontend Development
- Install React Compiler for enhanced performance (optional)
- Refer to [Vite Documentation](https://vitejs.dev/) for advanced configuration
- Check [React Documentation](https://react.dev/) for best practices

## Troubleshooting

### Port Already in Use
If port 7860 is already in use, update the configuration in `app.py` or the Docker command.

### Module Not Found Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
cd frontend && npm install
```

## Resources

- [FastHTML Documentation](https://fastht.ml/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Docker Documentation](https://docs.docker.com/)

---

**Status**: Active Development | **Last Updated**: July 2026
