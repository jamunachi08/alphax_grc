# Copyright (c) 2026, Neotec Integrated Solutions
import frappe
from frappe.model.document import Document

THEMES = [
	"Ocean",
	"Sunset",
	"Forest",
	"Royal",
	"Desert",
	"Monochrome (No Colour)",
	"High Contrast",
]


class GRCPathwaySettings(Document):
	def validate(self):
		if self.color_theme not in THEMES:
			frappe.throw(f"Unknown colour theme: {self.color_theme}")
