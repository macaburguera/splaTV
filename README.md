# **SplaTV - Dynamic Splatting Real-Time Visualizer**

This repository is a fork of the original SplaTV by [@antimatter15](https://github.com/antimatter15). It includes additional code for converting standard `.ply` files (SpacetimeGaussian format) into `.splatv` format, which is used by the visualizer. It also contains extra `.splatv` recreations.

---

## **Installation Instructions**

1. Update your system and install Node.js and npm:
   ```bash
   sudo apt update
   sudo apt install -y nodejs npm
   ```

2. Clone the repository and navigate into it:
   ```bash
   git clone https://github.com/macaburguera/splaTV.git
   cd splaTV
   ```

3. Install the required dependencies:
   ```bash
   npm install
   ```

---

## **Usage**

### **Converting `.ply` to `.splatv`**

Use the provided Python script to convert SpacetimeGaussians `.ply` files into `.splatv` format:
```bash
python ply_to_splatv.py /path/to/ply --output /path/to/splatv/output
```

### **Running the Visualizer**

1. Start the interface:
   ```bash
   npm start
   ```

   The visualizer will be running at `http://localhost:3000`.

2. By default, the visualizer loads `model.splatv` (included in the original SplaTV repository).  
   Once the interface opens, you can select any `.splatv` file from your local machine using the visual interface.

3. **Troubleshooting:**  
   If the visual interface fails to load the selected file, you can hardcode the path to the desired `.splatv` file directly in `hybrid.js` (around line **10006**):
   ```javascript
   const url = "splatv/model.splatv"; // Default file path
   ```

---

## **Additional Models**

Feel free to explore the provided `.splatv` models under the `/splatv` folder. These examples can be used to test and experiment with the visualizer.
