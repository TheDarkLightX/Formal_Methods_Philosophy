#!/usr/bin/env python3
"""Build and render the ZRPF visual tutorial with Blender.

Run through Blender so ``bpy`` is available:

    blender --background --factory-startup \
      --python scripts/blender/render_zrpf_tutorial.py -- \
      --project-root . --render-stills --render-video

The saved Blend file uses only built-in geometry, materials, and fonts. The
scene is an explanatory model. Status badges distinguish current local
evidence, proposed architecture, and benchmark-dependent targets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


FPS = 24
FRAME_END = 1152
CAMERA_Y = -30.0
TEXT_Y = -0.46
PANEL_Y = 0.0
LINE_Y = 0.38

COLORS = {
    "background": "07111F",
    "panel": "101D32",
    "panel_alt": "16243B",
    "grid": "1D3554",
    "white": "F8FAFC",
    "muted": "94A3B8",
    "cyan": "22D3EE",
    "blue": "3B82F6",
    "violet": "A78BFA",
    "green": "34D399",
    "amber": "F59E0B",
    "red": "FB7185",
}


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--render-stills", action="store_true")
    parser.add_argument("--render-video", action="store_true")
    parser.add_argument("--preview", action="store_true")
    return parser.parse_args(argv)


def rgb(hex_color: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    value = hex_color.lstrip("#")
    return tuple(int(value[i : i + 2], 16) / 255.0 for i in (0, 2, 4)) + (alpha,)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.curves,
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def make_material(
    name: str,
    color: str,
    *,
    metallic: float = 0.0,
    roughness: float = 0.42,
    emission: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    rgba = rgb(color)
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    emission_input = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    strength_input = bsdf.inputs.get("Emission Strength")
    if emission_input is not None:
        emission_input.default_value = rgba
    if strength_input is not None:
        strength_input.default_value = emission
    return material


def setup_scene() -> tuple[bpy.types.Scene, dict[str, bpy.types.Material]]:
    clear_scene()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = FRAME_END
    scene.render.use_file_extension = True
    scene.eevee.taa_render_samples = 16

    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass

    world = bpy.data.worlds.new("ZRPF World") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = rgb(
        COLORS["background"]
    )
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.22

    materials = {
        "background": make_material("Background", COLORS["background"], roughness=0.72),
        "panel": make_material("Panel", COLORS["panel"], metallic=0.18, roughness=0.32),
        "panel_alt": make_material(
            "Panel Alt", COLORS["panel_alt"], metallic=0.12, roughness=0.36
        ),
        "grid": make_material("Grid", COLORS["grid"], emission=0.22),
        "white": make_material("White", COLORS["white"], emission=0.9),
        "muted": make_material("Muted", COLORS["muted"], emission=0.45),
        "cyan": make_material(
            "Cyan", COLORS["cyan"], metallic=0.25, roughness=0.25, emission=1.2
        ),
        "blue": make_material(
            "Blue", COLORS["blue"], metallic=0.25, roughness=0.25, emission=0.8
        ),
        "violet": make_material(
            "Violet", COLORS["violet"], metallic=0.22, roughness=0.25, emission=0.9
        ),
        "green": make_material(
            "Green", COLORS["green"], metallic=0.2, roughness=0.25, emission=1.0
        ),
        "amber": make_material(
            "Amber", COLORS["amber"], metallic=0.2, roughness=0.25, emission=0.9
        ),
        "red": make_material(
            "Red", COLORS["red"], metallic=0.2, roughness=0.25, emission=0.9
        ),
    }

    bpy.ops.object.camera_add(location=(0.0, CAMERA_Y, 0.0))
    camera = bpy.context.object
    camera.name = "ZRPF Camera"
    camera.data.type = "ORTHO"
    # Blender's orthographic scale is the horizontal span for this camera
    # orientation. 15.8 keeps the full 16:9 teaching canvas in frame.
    camera.data.ortho_scale = 15.8
    camera.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    scene.camera = camera

    add_area_light("Key", (0.0, -8.0, 5.5), 1150.0, 11.0)
    add_area_light("Fill", (-6.0, -4.0, -2.0), 650.0, 8.0)
    add_area_light("Rim", (6.0, 3.0, 4.0), 900.0, 7.0, face_negative_y=True)

    add_box(
        "Backdrop",
        (0.0, 1.8, 0.0),
        (17.0, 0.22, 9.6),
        materials["background"],
        bevel=0.18,
    )
    build_grid(materials["grid"])
    return scene, materials


def add_area_light(
    name: str,
    location: tuple[float, float, float],
    energy: float,
    size: float,
    *,
    face_negative_y: bool = False,
) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(light)
    light.location = location
    light.rotation_euler = (
        math.radians(-90.0 if face_negative_y else 90.0),
        0.0,
        0.0,
    )
    return light


def add_box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    *,
    bevel: float = 0.12,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        modifier = obj.modifiers.new("Rounded edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 4
    obj.data.materials.append(material)
    return obj


def add_sphere(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def add_torus(
    name: str,
    location: tuple[float, float, float],
    major_radius: float,
    minor_radius: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=64,
        minor_segments=16,
        location=location,
        rotation=(math.radians(90.0), 0.0, 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def add_text(
    name: str,
    body: str,
    location: tuple[float, float, float],
    material: bpy.types.Material,
    *,
    size: float = 0.42,
    align: str = "CENTER",
    extrude: float = 0.012,
    line_spacing: float = 0.9,
) -> bpy.types.Object:
    bpy.ops.object.text_add(location=location, rotation=(math.radians(90.0), 0.0, 0.0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = body
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = extrude
    obj.data.bevel_depth = 0.004
    obj.data.bevel_resolution = 3
    obj.data.space_line = line_spacing
    obj.data.materials.append(material)
    return obj


def add_line(
    name: str,
    start: tuple[float, float],
    end: tuple[float, float],
    material: bpy.types.Material,
    *,
    width: float = 0.035,
    frame_start: int | None = None,
    frame_end: int | None = None,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = width
    curve.bevel_resolution = 4
    spline = curve.splines.new("POLY")
    spline.points.add(1)
    spline.points[0].co = (start[0], LINE_Y, start[1], 1.0)
    spline.points[1].co = (end[0], LINE_Y, end[1], 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    if frame_start is not None and frame_end is not None:
        curve.bevel_factor_end = 0.0
        curve.keyframe_insert("bevel_factor_end", frame=frame_start)
        curve.bevel_factor_end = 1.0
        curve.keyframe_insert("bevel_factor_end", frame=frame_end)
    return obj


def build_grid(material: bpy.types.Material) -> None:
    for x in range(-7, 8):
        obj = add_line(f"Grid V {x}", (x, -4.2), (x, 4.2), material, width=0.006)
        obj.location.y = 1.1
    for z_index in range(-4, 5):
        obj = add_line(
            f"Grid H {z_index}", (-7.7, z_index), (7.7, z_index), material, width=0.006
        )
        obj.location.y = 1.1


def add_card(
    name: str,
    center: tuple[float, float],
    size: tuple[float, float],
    title: str,
    subtitle: str,
    materials: dict[str, bpy.types.Material],
    accent: str,
    *,
    title_size: float = 0.31,
    subtitle_size: float = 0.19,
) -> list[bpy.types.Object]:
    x, z = center
    width, height = size
    objects = [
        add_box(
            f"{name} Panel",
            (x, PANEL_Y, z),
            (width, 0.34, height),
            materials["panel"],
            bevel=min(0.16, height * 0.18),
        ),
        add_box(
            f"{name} Accent",
            (x - width / 2 + 0.08, -0.22, z),
            (0.10, 0.06, height * 0.72),
            materials[accent],
            bevel=0.045,
        ),
        add_text(
            f"{name} Title",
            title,
            (x + 0.08, TEXT_Y, z + (0.14 if subtitle else 0.0)),
            materials["white"],
            size=title_size,
        ),
    ]
    if subtitle:
        objects.append(
            add_text(
                f"{name} Subtitle",
                subtitle,
                (x + 0.08, TEXT_Y - 0.01, z - 0.23),
                materials["muted"],
                size=subtitle_size,
                line_spacing=0.82,
            )
        )
    return objects


def add_badge(
    name: str,
    center: tuple[float, float],
    label: str,
    materials: dict[str, bpy.types.Material],
    color: str,
    *,
    width: float | None = None,
) -> list[bpy.types.Object]:
    width = width or max(1.6, 0.115 * len(label) + 0.55)
    panel = add_box(
        f"{name} Badge",
        (center[0], -0.08, center[1]),
        (width, 0.20, 0.48),
        materials[color],
        bevel=0.22,
    )
    text = add_text(
        f"{name} Badge Text",
        label,
        (center[0], TEXT_Y - 0.08, center[1]),
        materials["background"],
        size=0.20,
        extrude=0.008,
    )
    return [panel, text]


def add_scene_title(
    prefix: str,
    title: str,
    subtitle: str,
    materials: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    objects = [
        add_text(
            f"{prefix} Title",
            title,
            (0.0, TEXT_Y, 3.55),
            materials["white"],
            size=0.60,
        )
    ]
    if subtitle:
        objects.append(
            add_text(
                f"{prefix} Subtitle",
                subtitle,
                (0.0, TEXT_Y, 2.92),
                materials["muted"],
                size=0.25,
            )
        )
    return objects


def active_between(obj: bpy.types.Object, start: int, end: int) -> None:
    obj.hide_render = True
    obj.keyframe_insert("hide_render", frame=max(0, start - 1))
    obj.hide_render = False
    obj.keyframe_insert("hide_render", frame=start)
    obj.hide_render = False
    obj.keyframe_insert("hide_render", frame=end)
    obj.hide_render = True
    obj.keyframe_insert("hide_render", frame=end + 1)


def pop_between(
    objects: list[bpy.types.Object],
    start: int,
    end: int,
    *,
    stagger: int = 0,
) -> None:
    for index, obj in enumerate(objects):
        local_start = start + index * stagger
        active_between(obj, local_start, end)
        final_scale = obj.scale.copy()
        obj.scale = final_scale * 0.001
        obj.keyframe_insert("scale", frame=local_start)
        obj.scale = final_scale
        obj.keyframe_insert("scale", frame=local_start + 10)
        obj.scale = final_scale
        obj.keyframe_insert("scale", frame=max(local_start + 11, end - 8))
        obj.scale = final_scale * 0.001
        obj.keyframe_insert("scale", frame=end)


def show_between(objects: list[bpy.types.Object], start: int, end: int) -> None:
    for obj in objects:
        active_between(obj, start, end)


def animate_pulse(
    name: str,
    start: tuple[float, float],
    end: tuple[float, float],
    material: bpy.types.Material,
    frame_start: int,
    frame_end: int,
    scene_end: int,
) -> bpy.types.Object:
    pulse = add_sphere(name, (start[0], -0.34, start[1]), 0.10, material)
    active_between(pulse, frame_start, scene_end)
    pulse.location = (start[0], -0.34, start[1])
    pulse.keyframe_insert("location", frame=frame_start)
    pulse.location = (end[0], -0.34, end[1])
    pulse.keyframe_insert("location", frame=frame_end)
    pulse.scale = (1.0, 1.0, 1.0)
    pulse.keyframe_insert("scale", frame=frame_start)
    pulse.scale = (1.7, 1.7, 1.7)
    pulse.keyframe_insert("scale", frame=frame_end)
    return pulse


def build_scene_1(materials: dict[str, bpy.types.Material]) -> None:
    start, end = 1, 168
    title = add_scene_title(
        "S1",
        "ZRPF",
        "Zeno Recursive Proof Fabric",
        materials,
    )
    pop_between(title, start + 2, end)
    stages = [
        ("EXECUTION", "ZenoDEX transition", "blue"),
        ("PROOF TASK", "bounded statement", "amber"),
        ("LEAF", "authenticated receipt", "cyan"),
        ("ROOT", "recursive summary", "cyan"),
        ("ADMISSION", "governed commit", "green"),
    ]
    xs = [-5.75, -2.9, 0.0, 2.9, 5.75]
    card_groups: list[list[bpy.types.Object]] = []
    for index, ((title_text, subtitle, accent), x) in enumerate(zip(stages, xs)):
        group = add_card(
            f"S1 Stage {index}",
            (x, 0.0),
            (2.25, 1.25),
            title_text,
            subtitle,
            materials,
            accent,
            title_size=0.27,
            subtitle_size=0.16,
        )
        pop_between(group, start + 28 + index * 15, end)
        card_groups.append(group)
    for index in range(len(xs) - 1):
        line = add_line(
            f"S1 Link {index}",
            (xs[index] + 1.1, 0.0),
            (xs[index + 1] - 1.1, 0.0),
            materials["cyan" if index in (1, 2) else "amber"],
            frame_start=start + 45 + index * 15,
            frame_end=start + 58 + index * 15,
        )
        active_between(line, start + 40 + index * 15, end)
        animate_pulse(
            f"S1 Pulse {index}",
            (xs[index] + 1.1, 0.0),
            (xs[index + 1] - 1.1, 0.0),
            materials["white"],
            start + 52 + index * 15,
            start + 64 + index * 15,
            end,
        )
    note = add_text(
        "S1 Boundary",
        "FULL PATH: PROPOSED ARCHITECTURE  •  BOUNDED STRUCTURAL SUBTREE: CURRENT LOCAL EVIDENCE",
        (0.0, TEXT_Y, -2.35),
        materials["muted"],
        size=0.21,
    )
    pop_between([note], start + 105, end)
    badge = add_badge("S1 Status", (0.0, -3.25), "CLAIM STATUS STAYS VISIBLE", materials, "amber")
    pop_between(badge, start + 118, end)


def build_scene_2(materials: dict[str, bpy.types.Material]) -> None:
    start, end = 169, 360
    pop_between(
        add_scene_title(
            "S2",
            "The evidenced structural tree",
            "Four Spot compatibility receipts, two structural levels, one authenticated root",
            materials,
        ),
        start + 2,
        end,
    )
    badge = add_badge(
        "S2 Evidence",
        (-5.45, 2.86),
        "CURRENT LOCAL EVIDENCE",
        materials,
        "cyan",
        width=3.5,
    )
    pop_between(badge, start + 10, end)
    warning = add_badge(
        "S2 Boundary",
        (5.55, 2.86),
        "STRUCTURAL PROFILE",
        materials,
        "amber",
        width=2.9,
    )
    pop_between(warning, start + 16, end)

    leaf_xs = [-5.4, -1.8, 1.8, 5.4]
    for index, x in enumerate(leaf_xs):
        card = add_card(
            f"S2 Leaf {index}",
            (x, -2.15),
            (2.25, 0.95),
            f"SPOT LEAF {index}",
            "NodeJournalV3 • level 0",
            materials,
            "cyan",
            title_size=0.24,
            subtitle_size=0.15,
        )
        pop_between(card, start + 32 + index * 9, end)

    level_one = [(-3.6, "L1 LEFT"), (3.6, "L1 RIGHT")]
    for index, (x, label) in enumerate(level_one):
        card = add_card(
            f"S2 {label}",
            (x, 0.05),
            (2.6, 1.05),
            label,
            "NodeJournalV3 • level 1",
            materials,
            "blue",
            title_size=0.28,
            subtitle_size=0.16,
        )
        pop_between(card, start + 92 + index * 8, end)

    root = add_card(
        "S2 Root",
        (0.0, 2.05),
        (2.9, 1.05),
        "L2 ROOT",
        "NodeJournalV3 • level 2",
        materials,
        "green",
        title_size=0.30,
        subtitle_size=0.16,
    )
    pop_between(root, start + 137, end)

    links = [
        ((-5.4, -1.68), (-3.6, -0.48)),
        ((-1.8, -1.68), (-3.6, -0.48)),
        ((1.8, -1.68), (3.6, -0.48)),
        ((5.4, -1.68), (3.6, -0.48)),
        ((-3.6, 0.58), (0.0, 1.52)),
        ((3.6, 0.58), (0.0, 1.52)),
    ]
    for index, (p1, p2) in enumerate(links):
        link_start = start + (70 if index < 4 else 120) + index * 3
        line = add_line(
            f"S2 Link {index}",
            p1,
            p2,
            materials["cyan" if index < 4 else "green"],
            frame_start=link_start,
            frame_end=link_start + 14,
        )
        active_between(line, link_start, end)

    facts = add_text(
        "S2 Facts",
        "4 SOURCE-TRANSITION RECEIPTS  •  7 NODES  •  DEPTH 2  •  SUCCESSFUL VERIFIER REPLAY",
        (0.0, TEXT_Y, -3.34),
        materials["white"],
        size=0.21,
    )
    boundary = add_text(
        "S2 Nonclaim",
        "No semantic conservation, DA, settlement, privacy, or production claim",
        (0.0, TEXT_Y, -3.73),
        materials["amber"],
        size=0.18,
    )
    pop_between([facts, boundary], start + 150, end, stagger=5)


def build_scene_3(materials: dict[str, bpy.types.Material]) -> None:
    start, end = 361, 528
    pop_between(
        add_scene_title(
            "S3",
            "One journal shape at every level",
            "A root can become a child because leaves and aggregates share one typed interface",
            materials,
        ),
        start + 2,
        end,
    )
    leaf = add_card(
        "S3 Leaf",
        (-5.5, 0.0),
        (2.35, 1.35),
        "LEAF",
        "level = 0\nchild_count = 0",
        materials,
        "cyan",
        title_size=0.31,
        subtitle_size=0.17,
    )
    aggregate = add_card(
        "S3 Aggregate",
        (5.5, 0.0),
        (2.35, 1.35),
        "AGGREGATE",
        "level > 0\nverified children",
        materials,
        "blue",
        title_size=0.27,
        subtitle_size=0.17,
    )
    pop_between(leaf, start + 25, end)
    pop_between(aggregate, start + 32, end)

    panel = add_box(
        "S3 Journal Panel",
        (0.0, PANEL_Y, -0.05),
        (5.45, 0.38, 5.25),
        materials["panel_alt"],
        bevel=0.24,
    )
    header_strip = add_box(
        "S3 Journal Header Strip",
        (0.0, -0.24, 2.1),
        (4.95, 0.07, 0.12),
        materials["cyan"],
        bevel=0.05,
    )
    header = add_text(
        "S3 Journal Header",
        "NodeJournalV3",
        (0.0, TEXT_Y, 2.43),
        materials["white"],
        size=0.42,
    )
    pop_between([panel, header_strip, header], start + 42, end, stagger=3)
    rows = [
        (1.42, "SCOPE", "application • domain • epoch • policy"),
        (0.65, "COUNTS + PARTITION", "level • leaves • operations • dense range"),
        (-0.12, "IDENTITY", "task • program • derived verifier • profile"),
        (-0.89, "23 COMMITMENTS", "state • effects • receipts • DA • carry • schedule"),
        (-1.66, "CHILD ROOTS", "claims • journals • programs • manifests • provenance"),
    ]
    for index, (z, label, detail) in enumerate(rows):
        row = add_box(
            f"S3 Row {index}",
            (0.0, -0.21, z),
            (4.65, 0.08, 0.58),
            materials["panel"],
            bevel=0.12,
        )
        label_text = add_text(
            f"S3 Row Label {index}",
            label,
            (-2.05, TEXT_Y - 0.04, z),
            materials["cyan"],
            size=0.18,
            align="LEFT",
        )
        detail_text = add_text(
            f"S3 Row Detail {index}",
            detail,
            (0.08, TEXT_Y - 0.04, z),
            materials["muted"],
            size=0.13,
            align="LEFT",
        )
        pop_between([row, label_text, detail_text], start + 60 + index * 10, end)

    for index, (p1, p2) in enumerate(
        [((-4.3, 0.0), (-2.75, 0.0)), ((4.3, 0.0), (2.75, 0.0))]
    ):
        line = add_line(
            f"S3 Interface Link {index}",
            p1,
            p2,
            materials["cyan"],
            frame_start=start + 50,
            frame_end=start + 70,
        )
        active_between(line, start + 50, end)
    note = add_text(
        "S3 Boundary",
        "STRUCTURAL VALIDITY ≠ APPLICATION SEMANTICS",
        (0.0, TEXT_Y, -3.45),
        materials["amber"],
        size=0.23,
    )
    pop_between([note], start + 116, end)


def build_scene_4(materials: dict[str, bpy.types.Material]) -> None:
    start, end = 529, 696
    pop_between(
        add_scene_title(
            "S4",
            "Proof and availability are separate obligations",
            "A commitment to data does not establish that anyone can retrieve the data",
            materials,
        ),
        start + 2,
        end,
    )
    proof = add_card(
        "S4 Proof",
        (-3.8, 1.15),
        (4.0, 1.55),
        "PROOF RAIL",
        "receipt verified\nexact journal bound",
        materials,
        "cyan",
        title_size=0.31,
        subtitle_size=0.18,
    )
    availability = add_card(
        "S4 DA",
        (3.8, 1.15),
        (4.0, 1.55),
        "AVAILABILITY RAIL",
        "data root + certificate\nretrieval policy checked",
        materials,
        "violet",
        title_size=0.28,
        subtitle_size=0.18,
    )
    pop_between(proof, start + 28, end)
    pop_between(availability, start + 38, end)
    proof_badge = add_badge("S4 Proof Status", (-3.8, -0.18), "CURRENT STRUCTURAL CHECK", materials, "cyan", width=3.7)
    da_badge = add_badge("S4 DA Status", (3.8, -0.18), "VERIFICATION PENDING", materials, "amber", width=3.2)
    pop_between(proof_badge, start + 55, end)
    pop_between(da_badge, start + 62, end)

    gate = add_card(
        "S4 Gate",
        (0.0, -2.05),
        (4.2, 1.25),
        "LEDGER ADMISSION",
        "proof_ok ∧ da_policy_ok ∧ governed_bindings_ok",
        materials,
        "green",
        title_size=0.30,
        subtitle_size=0.16,
    )
    pop_between(gate, start + 104, end)
    for index, (p1, p2, color) in enumerate(
        [((-3.8, 0.38), (-1.2, -1.43), "cyan"), ((3.8, 0.38), (1.2, -1.43), "violet")]
    ):
        line = add_line(
            f"S4 Rail {index}",
            p1,
            p2,
            materials[color],
            frame_start=start + 72 + index * 6,
            frame_end=start + 94 + index * 6,
            width=0.055,
        )
        active_between(line, start + 70, end)
        animate_pulse(
            f"S4 Pulse {index}",
            p1,
            p2,
            materials[color],
            start + 80 + index * 6,
            start + 100 + index * 6,
            end,
        )
    note = add_text(
        "S4 Boundary",
        "CURRENT JOURNALS COMMIT DA ROOTS; CURRENT STRUCTURAL EVIDENCE DOES NOT VERIFY DA",
        (0.0, TEXT_Y, -3.35),
        materials["amber"],
        size=0.19,
    )
    pop_between([note], start + 120, end)


def build_scene_5(materials: dict[str, bpy.types.Material]) -> None:
    start, end = 697, 864
    pop_between(
        add_scene_title(
            "S5",
            "Authority moves through verification",
            "Proof-looking bytes gain authority only after the required gates accept them",
            materials,
        ),
        start + 2,
        end,
    )
    stages = [
        (-5.65, "PROVER BYTES", "proposes", "amber"),
        (-1.9, "GUEST", "verifies child receipt\nbefore journal decode", "cyan"),
        (1.9, "HOST", "verifies receipt + journal\n+ program equality", "blue"),
        (5.65, "LEDGER POLICY", "checks governed bindings", "green"),
    ]
    for index, (x, title, subtitle, accent) in enumerate(stages):
        card = add_card(
            f"S5 Stage {index}",
            (x, 0.65),
            (2.8, 1.55),
            title,
            subtitle,
            materials,
            accent,
            title_size=0.25,
            subtitle_size=0.16,
        )
        pop_between(card, start + 28 + index * 17, end)
    for index in range(3):
        p1 = (stages[index][0] + 1.4, 0.65)
        p2 = (stages[index + 1][0] - 1.4, 0.65)
        line = add_line(
            f"S5 Link {index}",
            p1,
            p2,
            materials["cyan" if index < 2 else "green"],
            frame_start=start + 52 + index * 18,
            frame_end=start + 65 + index * 18,
        )
        active_between(line, start + 50 + index * 18, end)
        animate_pulse(
            f"S5 Pulse {index}",
            p1,
            p2,
            materials["white"],
            start + 57 + index * 18,
            start + 69 + index * 18,
            end,
        )
    current = add_badge("S5 Current", (0.0, 2.02), "GUEST + SEALED HOST: CURRENT PROFILE", materials, "cyan", width=5.2)
    proposed = add_badge("S5 Proposed", (5.65, 2.02), "PROPOSED", materials, "amber", width=1.85)
    pop_between(current, start + 80, end)
    pop_between(proposed, start + 95, end)

    reject = add_card(
        "S5 Reject",
        (0.0, -2.05),
        (3.5, 1.05),
        "REJECT → NO-OP",
        "wrong image • substituted journal • missing assumption",
        materials,
        "red",
        title_size=0.29,
        subtitle_size=0.15,
    )
    pop_between(reject, start + 112, end)
    reject_line = add_line(
        "S5 Reject Line",
        (-1.9, -0.13),
        (0.0, -1.52),
        materials["red"],
        frame_start=start + 106,
        frame_end=start + 123,
        width=0.055,
    )
    active_between(reject_line, start + 104, end)
    formula = add_text(
        "S5 Formula",
        "reject  ⇒  state′ = state  ∧  replay′ = replay  ∧  rewards′ = rewards",
        (0.0, TEXT_Y, -3.38),
        materials["white"],
        size=0.22,
    )
    pop_between([formula], start + 132, end)


def build_scene_6(materials: dict[str, bpy.types.Material]) -> None:
    start, end = 865, 1032
    pop_between(
        add_scene_title(
            "S6",
            "Admission must commit one atomic bundle",
            "A crash must not separate value effects from replay protection or proof-market accounting",
            materials,
        ),
        start + 2,
        end,
    )
    ring = add_torus("S6 Atomic Ring", (0.0, -0.02, 0.0), 1.22, 0.14, materials["green"])
    core = add_text(
        "S6 Atomic Core",
        "ATOMIC\nCOMMIT",
        (0.0, TEXT_Y - 0.05, 0.0),
        materials["white"],
        size=0.32,
        line_spacing=0.78,
    )
    pop_between([ring, core], start + 44, end, stagger=3)
    items = [
        ((-5.25, 1.55), "STATE ROOT", "application state", "blue"),
        ((0.0, 2.15), "REPLAY SETS", "root • child • receipt • message", "cyan"),
        ((5.25, 1.55), "CARRY QUEUE", "pre/post continuity", "violet"),
        ((-5.25, -1.35), "DA ROOT", "certificate binding", "violet"),
        ((5.25, -1.35), "PAYOUTS", "rewards + slashes", "amber"),
    ]
    for index, (center, title, subtitle, accent) in enumerate(items):
        card = add_card(
            f"S6 Item {index}",
            center,
            (3.05, 1.05),
            title,
            subtitle,
            materials,
            accent,
            title_size=0.25,
            subtitle_size=0.15,
        )
        pop_between(card, start + 24 + index * 7, end)
        target_x = 1.25 if center[0] < 0 else (-1.25 if center[0] > 0 else 0.0)
        target_z = 0.55 if center[1] > 0 else -0.55
        if center[0] == 0:
            target_z = 1.25
        line = add_line(
            f"S6 Link {index}",
            center,
            (target_x, target_z),
            materials[accent],
            frame_start=start + 64 + index * 4,
            frame_end=start + 84 + index * 4,
            width=0.045,
        )
        active_between(line, start + 60, end)
        animate_pulse(
            f"S6 Pulse {index}",
            center,
            (target_x, target_z),
            materials[accent],
            start + 76 + index * 4,
            start + 96 + index * 4,
            end,
        )

    statuses = [
        ("EXECUTED", "blue"),
        ("PROVEN", "cyan"),
        ("CHECKPOINTED", "violet"),
        ("FINALIZED", "green"),
    ]
    xs = [-5.25, -1.75, 1.75, 5.25]
    for index, ((label, color), x) in enumerate(zip(statuses, xs)):
        badge = add_badge(f"S6 Finality {index}", (x, -3.25), label, materials, color, width=2.55)
        pop_between(badge, start + 112 + index * 7, end)
        if index < 3:
            line = add_line(
                f"S6 Finality Link {index}",
                (x + 1.27, -3.25),
                (xs[index + 1] - 1.27, -3.25),
                materials["muted"],
                frame_start=start + 120 + index * 7,
                frame_end=start + 128 + index * 7,
                width=0.025,
            )
            active_between(line, start + 118, end)


def build_scene_7(materials: dict[str, bpy.types.Material]) -> None:
    start, end = 1033, 1152
    pop_between(
        add_scene_title(
            "S7",
            "Read the status before the claim",
            "ZRPF is easiest to understand when evidence, architecture, and targets stay separated",
            materials,
        ),
        start + 2,
        end,
    )
    columns = [
        (
            -4.9,
            "CURRENT EVIDENCE",
            "4 Spot adapter receipts\n2 structural levels\nexact child receipt checks\nverifier-only replay\ncompiled bound: 8 × 8",
            "cyan",
        ),
        (
            0.0,
            "PROPOSED SYSTEM",
            "semantic composition\nconflict scheduler\nDA verification\natomic ledger admission\nassigned proof market",
            "amber",
        ),
        (
            4.9,
            "BENCHMARK TARGETS",
            "819 TPS initial envelope\n~100k TPS scale envelope\nlatency and cost unknown\nbenchmarks required\nno production claim",
            "violet",
        ),
    ]
    for index, (x, heading, body, accent) in enumerate(columns):
        panel = add_box(
            f"S7 Panel {index}",
            (x, PANEL_Y, -0.15),
            (4.25, 0.38, 5.25),
            materials["panel_alt"],
            bevel=0.24,
        )
        strip = add_box(
            f"S7 Strip {index}",
            (x, -0.24, 2.1),
            (3.8, 0.07, 0.12),
            materials[accent],
            bevel=0.05,
        )
        title = add_text(
            f"S7 Heading {index}",
            heading,
            (x, TEXT_Y, 2.48),
            materials[accent],
            size=0.29,
        )
        body_text = add_text(
            f"S7 Body {index}",
            body,
            (x, TEXT_Y, -0.15),
            materials["white"],
            size=0.25,
            line_spacing=1.35,
        )
        pop_between([panel, strip, title, body_text], start + 24 + index * 12, end)
    closing = add_text(
        "S7 Closing",
        "STRUCTURE IS REAL • SEMANTICS ARE PARTIAL • PERFORMANCE REMAINS TO BE MEASURED",
        (0.0, TEXT_Y, -3.45),
        materials["amber"],
        size=0.20,
    )
    pop_between([closing], start + 68, end)


def add_timeline_markers(scene: bpy.types.Scene) -> None:
    markers = [
        (1, "Fabric overview"),
        (169, "Evidenced structural tree"),
        (361, "Common node journal"),
        (529, "Proof and data availability"),
        (697, "Verifier authority"),
        (865, "Atomic admission"),
        (1033, "Claim status"),
    ]
    for frame, name in markers:
        scene.timeline_markers.new(name, frame=frame)


def save_blend(scene: bpy.types.Scene, path: Path) -> None:
    scene.render.filepath = "//../videos/zrpf/zrpf-proof-fabric"
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(path))


def render_stills(scene: bpy.types.Scene, output_dir: Path, *, preview: bool) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stills = [
        ("zrpf-fabric-overview.png", 150),
        ("zrpf-evidenced-tree.png", 330),
        ("zrpf-common-journal.png", 500),
        ("zrpf-proof-vs-data-availability.png", 670),
        ("zrpf-verifier-authority.png", 840),
        ("zrpf-atomic-admission.png", 1010),
        ("zrpf-claim-status.png", 1125),
    ]
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.resolution_x = 1280 if preview else 1600
    scene.render.resolution_y = 720 if preview else 900
    rendered: list[Path] = []
    for filename, frame in stills:
        path = output_dir / filename
        scene.frame_set(frame)
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        rendered.append(path)
    return rendered


def render_video(scene: bpy.types.Scene, output_path: Path, *, preview: bool) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.resolution_x = 960 if preview else 1920
    scene.render.resolution_y = 540 if preview else 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.media_type = "VIDEO"
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM" if preview else "PERC_LOSSLESS"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD" if preview else "BEST"
    scene.render.ffmpeg.gopsize = 12
    scene.render.filepath = str(output_path.parent / f"{output_path.stem}-")
    scene.frame_start = 1
    scene.frame_end = FRAME_END
    scene.frame_step = 2 if preview else 1
    scene.render.fps = FPS // 2 if preview else FPS
    original_taa_samples = scene.eevee.taa_render_samples
    scene.eevee.taa_render_samples = 4
    if output_path.exists():
        output_path.unlink()
    for stale in output_path.parent.glob(f"{output_path.stem}-*.mp4"):
        stale.unlink()
    bpy.ops.render.render(animation=True)
    candidates = sorted(
        output_path.parent.glob(f"{output_path.stem}-*.mp4"),
        key=lambda path: path.stat().st_mtime_ns,
    )
    if len(candidates) != 1:
        raise RuntimeError(
            f"expected one rendered movie for {output_path.name}, found {len(candidates)}"
        )
    candidates[0].replace(output_path)
    scene.frame_step = 1
    scene.render.fps = FPS
    scene.eevee.taa_render_samples = original_taa_samples
    return output_path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(
    path: Path,
    blend_file: Path,
    stills: list[Path],
    video: Path | None,
    *,
    video_is_preview: bool,
) -> None:
    artifacts = []
    for artifact in [blend_file, *stills, *([video] if video and video.exists() else [])]:
        if artifact.exists():
            artifacts.append(
                {
                    "path": artifact.name,
                    "size_bytes": artifact.stat().st_size,
                    "sha256": sha256(artifact),
                }
            )
    payload = {
        "schema": "formal_philosophy/zrpf_blender_render_manifest/v1",
        "blender_version": bpy.app.version_string,
        "fps": FPS,
        "frame_end": FRAME_END,
        "duration_seconds": FRAME_END / FPS,
        "video_profile": {
            "width": 960 if video_is_preview else 1920,
            "height": 540 if video_is_preview else 1080,
            "encoded_fps": FPS // 2 if video_is_preview else FPS,
        },
        "claim_status_palette": {
            "cyan": "current authenticated structural information",
            "violet": "data-availability information",
            "green": "accepted complete gate",
            "red": "rejection and no-op",
            "amber": "proposal or benchmark-dependent target",
        },
        "artifacts": artifacts,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = args.project_root.expanduser().resolve()
    scene, materials = setup_scene()
    if args.preview:
        scene.eevee.taa_render_samples = 4
    build_scene_1(materials)
    build_scene_2(materials)
    build_scene_3(materials)
    build_scene_4(materials)
    build_scene_5(materials)
    build_scene_6(materials)
    build_scene_7(materials)
    add_timeline_markers(scene)

    blend_file = root / "assets" / "blender" / "zrpf-proof-fabric.blend"
    still_dir = root / "assets" / "images" / "zrpf"
    video_path = root / "assets" / "videos" / "zrpf" / "zrpf-proof-fabric.mp4"
    save_blend(scene, blend_file)

    rendered_stills: list[Path] = []
    if args.render_stills:
        rendered_stills = render_stills(scene, still_dir, preview=args.preview)
    rendered_video: Path | None = None
    if args.render_video:
        rendered_video = render_video(scene, video_path, preview=args.preview)

    save_blend(scene, blend_file)
    manifest_stills = rendered_stills or [
        path
        for path in sorted(still_dir.glob("zrpf-*.png"))
        if path.is_file()
    ]
    manifest_video = rendered_video or (video_path if video_path.exists() else None)
    write_manifest(
        still_dir / "render-manifest.json",
        blend_file,
        manifest_stills,
        manifest_video,
        video_is_preview=args.preview and rendered_video is not None,
    )
    print(
        json.dumps(
            {
                "ok": True,
                "blend_file": str(blend_file),
                "stills": [str(path) for path in rendered_stills],
                "video": str(rendered_video) if rendered_video else None,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
