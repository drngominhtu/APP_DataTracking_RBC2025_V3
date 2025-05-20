from PyQt5 import QtWidgets, QtGui, QtCore
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import csv
import os
import time
from datetime import datetime
from config import MAP_WIDTH, MAP_HEIGHT, ROBOT_DIAMETER, MAX_DATA_POINTS

# Tạo lớp GraphWidget từ đầu hoặc import từ file riêng
from graph_widget import GraphWidget

class Visualization(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        # Data storage - Phải khởi tạo trước khi setup các component
        self.data_history = {}
        self.max_history = MAX_DATA_POINTS
        self.next_graph_id = 1
        self.graphs = []
        
        # Main layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(2)  # Giảm khoảng cách
        self.layout.setContentsMargins(2, 2, 2, 2)  # Giảm margin
        self.setLayout(self.layout)
        
        # Tạo layout cho nội dung chính
        main_content_layout = QtWidgets.QHBoxLayout()
        
        # Tạo container cho bên trái (graphs)
        left_container = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_container)
        left_layout.setContentsMargins(1, 1, 1, 1)
        left_layout.setSpacing(2)
        
        # Tạo container cho bên phải (table và map)
        right_container = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_container)
        right_layout.setContentsMargins(1, 1, 1, 1)
        right_layout.setSpacing(2)
        
        # Thêm các container vào main content
        main_content_layout.addWidget(left_container, 8)  # 80% width
        main_content_layout.addWidget(right_container, 2)  # 20% width
        
        # Thêm main content vào layout chính
        self.layout.addLayout(main_content_layout)
        
        # Tạo scroll area cho biểu đồ ở bên trái
        self.graphs_scroll = QtWidgets.QScrollArea()
        self.graphs_scroll.setWidgetResizable(True)
        self.graphs_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.graphs_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        
        # Tạo container cho các biểu đồ
        self.graphs_container = QtWidgets.QWidget()
        self.graphs_layout = QtWidgets.QVBoxLayout(self.graphs_container)
        self.graphs_layout.setContentsMargins(1, 1, 1, 1)
        self.graphs_layout.setSpacing(2)
        
        # Set container vào scroll area
        self.graphs_scroll.setWidget(self.graphs_container)
        
        # Thêm nút "Add New Graph" và scroll area vào left layout
        left_layout.addWidget(QtWidgets.QLabel("Graphs"), 0)
        
        add_graph_button = QtWidgets.QPushButton("Add New Graph")
        add_graph_button.clicked.connect(self.add_new_graph)
        add_graph_button.setFixedHeight(25)
        left_layout.addWidget(add_graph_button, 0)
        
        left_layout.addWidget(self.graphs_scroll, 1)  # 1 là stretch factor
        
        # Thêm bảng vào right layout (top)
        self.table_container = QtWidgets.QWidget()
        self.table_layout = QtWidgets.QVBoxLayout(self.table_container)
        self.table_layout.setContentsMargins(1, 1, 1, 1)
        self.table_layout.setSpacing(2)
        
        # Setup table
        right_layout.addWidget(QtWidgets.QLabel("Data Table"), 0)
        self.setup_table()
        right_layout.addWidget(self.table_container, 5)  # 5 là stretch factor: 50% của right container
        
        # Thêm map vào right layout (bottom)
        self.map_container = QtWidgets.QWidget()
        self.map_layout = QtWidgets.QVBoxLayout(self.map_container)
        self.map_layout.setContentsMargins(1, 1, 1, 1)
        self.map_layout.setSpacing(2)
        
        # Setup map
        right_layout.addWidget(QtWidgets.QLabel("Position Map"), 0)
        self.setup_map()
        right_layout.addWidget(self.map_container, 5)  # 5 là stretch factor: 50% của right container
        
        # Tạo biểu đồ đầu tiên
        self.add_new_graph()

    def setup_graphs(self):
        # Không cần phương thức này nữa vì đã xử lý trong __init__
        pass
    
    def add_new_graph(self):
        """Add a new graph widget"""
        # Remove spacer if it exists (to add it back later)
        spacer_item = self.graphs_layout.takeAt(self.graphs_layout.count() - 1) if self.graphs_layout.count() > 0 else None
        
        graph_widget = GraphWidget(self, self.next_graph_id)
        self.graphs.append(graph_widget)
        self.graphs_layout.addWidget(graph_widget)
        self.next_graph_id += 1
        
        # Add back spacer at the end
        if spacer_item:
            self.graphs_layout.addItem(spacer_item)
        else:
            self.graphs_layout.addStretch()
    
    def setup_table(self):
        # Create table widget with fixed height
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Topic", "Variable", "Value"])
        
        # Adjust column widths
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        
        # Giảm chiều cao mặc định của các hàng để hiển thị nhiều hàng hơn
        self.table.verticalHeader().setDefaultSectionSize(18)
        
        # Ẩn header dọc (số thứ tự hàng) để tiết kiệm không gian
        self.table.verticalHeader().setVisible(False)
        
        # Đặt kích thước bảng
        self.table.setMinimumHeight(200)
        
        # Giảm font size của nội dung bảng
        font = self.table.font()
        font.setPointSize(8)
        self.table.setFont(font)
        
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)  # Làm nổi bật các hàng
        
        # Add to layout - đặt bảng ở vị trí đầu tiên trong layout để nó ở trên cùng
        self.table_layout.addWidget(self.table)
        
        # Thu gọn filter box và đặt ở dưới bảng
        filter_widget = QtWidgets.QWidget()
        filter_layout = QtWidgets.QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(2)
        
        self.filter_label = QtWidgets.QLabel("Filter:")
        self.filter_input = QtWidgets.QLineEdit()
        self.filter_input.textChanged.connect(self.filter_table)
        
        # Thu nhỏ filter box
        self.filter_label.setFixedWidth(30)
        self.filter_input.setFixedHeight(20)
        
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_input)
        
        self.table_layout.addWidget(filter_widget)

    def setup_map(self):
        # Create canvas for position map
        self.map_figure = Figure(figsize=(3, 3), dpi=100)  # Giảm kích thước map
        self.map_canvas = FigureCanvas(self.map_figure)
        self.map_ax = self.map_figure.add_subplot(111)
        self.map_ax.set_title('Robot Position')
        self.map_ax.set_xlabel('X Position (m)')
        self.map_ax.set_ylabel('Y Position (m)')
        self.map_ax.grid(True)
        self.map_ax.set_xlim(0, MAP_WIDTH)
        self.map_ax.set_ylim(0, MAP_HEIGHT)
        self.map_ax.set_aspect('equal')
        
        # Initialize robot marker
        self.robot_marker, = self.map_ax.plot([], [], 'ro', markersize=10)
        self.trail_line, = self.map_ax.plot([], [], 'r-', alpha=0.5)
        self.trail_data = {'x': [], 'y': []}
        
        # Draw field rectangle
        field_rect = plt.Rectangle((0, 0), MAP_WIDTH, MAP_HEIGHT, fill=False, color='black')
        self.map_ax.add_patch(field_rect)
        
        # Add robot circle with correct diameter
        self.robot_circle = plt.Circle((0, 0), ROBOT_DIAMETER/2, fill=True, color='red', alpha=0.3)
        self.map_ax.add_patch(self.robot_circle)
        
        # Add to layout
        self.map_layout.addWidget(self.map_canvas)
        
        # Controls for map - thu gọn các điều khiển
        map_control = QtWidgets.QWidget()
        map_control_layout = QtWidgets.QHBoxLayout(map_control)
        map_control_layout.setContentsMargins(0, 0, 0, 0)
        map_control_layout.setSpacing(2)

        self.clear_trail_button = QtWidgets.QPushButton("Clear Trail")
        self.clear_trail_button.setFixedHeight(20)
        self.clear_trail_button.clicked.connect(self.clear_trail)
        map_control_layout.addWidget(self.clear_trail_button)
        
        self.trail_checkbox = QtWidgets.QCheckBox("Show Trail")
        self.trail_checkbox.setChecked(True)
        self.trail_checkbox.stateChanged.connect(self.update_trail_visibility)
        map_control_layout.addWidget(self.trail_checkbox)
        
        self.position_label = QtWidgets.QLabel("Position: (0.00, 0.00)")
        self.position_label.setFont(QtGui.QFont('', 8))
        map_control_layout.addWidget(self.position_label)
        
        self.map_layout.addWidget(map_control)
    
    def update(self, data_str):
        try:
            # Try to parse as JSON
            data = json.loads(data_str)
            
            # Update table with new data
            self.update_table(data)
            
            # Update data history
            self.update_history(data)
            
            # Update variable selectors for all graphs
            self.update_variable_selectors(data)
            
            # Update position map if data contains x/y coordinates
            self.update_position(data)
            
            # Update all active graphs with new data
            self.update_graphs(data)
            
        except json.JSONDecodeError:
            # If not JSON, try to handle as simple values
            print(f"Received non-JSON data: {data_str}")
            
            # Try to handle as floating point number
            try:
                value = float(data_str)
                # Create a simple data dict with the value
                data = {"value": value}
                
                # Update with this simple data
                self.update_table(data)
                self.update_history(data)
                self.update_variable_selectors(data)
                self.update_graphs(data)
                
            except ValueError:
                # Not a number either, use as string
                data = {"message": data_str}
                self.update_table(data)
    
    def update_table(self, data):
        if isinstance(data, dict):
            # Find existing rows and update or add new
            for key, value in data.items():
                found = False
                for row in range(self.table.rowCount()):
                    if self.table.item(row, 1) and self.table.item(row, 1).text() == key:
                        # Update existing row
                        self.table.item(row, 2).setText(str(value))
                        found = True
                        break
                
                if not found:
                    # Add new row
                    rowPosition = self.table.rowCount()
                    self.table.insertRow(rowPosition)
                    topic_item = QtWidgets.QTableWidgetItem("current")
                    key_item = QtWidgets.QTableWidgetItem(key)
                    value_item = QtWidgets.QTableWidgetItem(str(value))
                    self.table.setItem(rowPosition, 0, topic_item)
                    self.table.setItem(rowPosition, 1, key_item)
                    self.table.setItem(rowPosition, 2, value_item)
    
    def update_history(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                try:
                    # Try to convert to float for graphing
                    value = float(value)
                    
                    if key not in self.data_history:
                        self.data_history[key] = []
                    
                    self.data_history[key].append(value)
                    
                    # Limit history size
                    if len(self.data_history[key]) > self.max_history:
                        self.data_history[key].pop(0)
                        
                except (ValueError, TypeError):
                    # Skip non-numeric values
                    pass
    
    def update_variable_selectors(self, data):
        if isinstance(data, dict):
            numeric_variables = []
            for key, value in data.items():
                try:
                    # Only add if value is numeric
                    float(value)
                    numeric_variables.append(key)
                except (ValueError, TypeError):
                    pass
            
            # Update selectors in all graph widgets
            for graph in self.graphs:
                graph.update_variable_selector(numeric_variables)
    
    def update_graphs(self, data):
        """Update all graphs with new data"""
        if isinstance(data, dict):
            for key, value in data.items():
                try:
                    # Only process numeric values
                    float_value = float(value)
                    # Update all graph widgets
                    for graph in self.graphs:
                        graph.update_data(key, float_value)
                except (ValueError, TypeError):
                    # Skip non-numeric values
                    pass
    
    def update_position(self, data):
        # Check if we have position data
        has_update = False
        
        if 'x' in data and 'y' in data:
            try:
                x = float(data['x'])
                y = float(data['y'])
                has_update = True
            except (ValueError, TypeError):
                pass
        
        # Alternative key names
        elif 'position_x' in data and 'position_y' in data:
            try:
                x = float(data['position_x'])
                y = float(data['position_y'])
                has_update = True
            except (ValueError, TypeError):
                pass
        
        elif 'encoder_x' in data and 'encoder_y' in data:
            try:
                x = float(data['encoder_x'])
                y = float(data['encoder_y'])
                has_update = True
            except (ValueError, TypeError):
                pass
                
        # Update the position if we have data
        if has_update:
            # Update position label
            self.position_label.setText(f"Position: ({x:.2f}, {y:.2f})")
            
            # Update robot marker
            self.robot_marker.set_data([x], [y])
            
            # Update robot circle position
            self.robot_circle.center = (x, y)
            
            # Update trail
            if self.trail_checkbox.isChecked():
                self.trail_data['x'].append(x)
                self.trail_data['y'].append(y)
                
                # Limit trail length
                if len(self.trail_data['x']) > self.max_history:
                    self.trail_data['x'].pop(0)
                    self.trail_data['y'].pop(0)
                
                self.trail_line.set_data(self.trail_data['x'], self.trail_data['y'])
            
            # Redraw map
            self.map_canvas.draw()
    
    def filter_table(self):
        filter_text = self.filter_input.text().lower()
        
        for row in range(self.table.rowCount()):
            hide_row = True
            
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and filter_text in item.text().lower():
                    hide_row = False
                    break
            
            self.table.setRowHidden(row, hide_row)
    
    def clear_trail(self):
        self.trail_data = {'x': [], 'y': []}
        self.trail_line.set_data([], [])
        self.map_canvas.draw()
    
    def update_trail_visibility(self):
        self.trail_line.set_visible(self.trail_checkbox.isChecked())
        self.map_canvas.draw()