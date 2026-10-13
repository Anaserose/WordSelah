import random
import sys
import datetime
import tkinter as tk
from bible_api import BibleAPIError, get_verse, is_cached
from bible_verse import DECLARATIONS, REFERENCES

USER_NAME = "Ana"#Ana is a Placeholder the v2 will collect username

BG_TOP = "#5A3D28"
BG_BOTTOM = "#261A12"
GOLD = "#E2C682"
GOLD_SOFT = "#D9C79C"
GOLD_DARK = "#B38B49"
CREAM = "#F6F0DF"
INK = "#2B1D12"
REF_COLOR = "#8A5A2B"
MUTED = "#8A7A5E"
RED = "#9A3B32"

#fonts
TITLE_FONT = ("Georgia", 20, "bold")
SUBTITLE_FONT = ("Georgia", 13, "italic")
PILL_FONT = ("Helvetica", 11, "bold")
REF_FONT = ("Georgia", 16, "bold")
VERSE_FONT = ("Georgia", 17, "italic")
LABEL_FONT = ("Helvetica", 11, "bold")
DECL_FONT = ("Georgia", 16)
FOOTER_FONT = ("Helvetica", 12)
BUTTON_FONT = ("Georgia", 16, "bold")
STAT_FONT = ("Georgia", 22, "bold")
STAT_LABEL_FONT = ("Helvetica", 12)
STAT_LABELS = ["Read", "Saved", "Day of the year"]

#sizes
WIDTH = 560
CARD_LEFT = 32
CARD_RIGHT = 528
PAD = 30                                   # the space between the card edge and the text
TEXT_X = CARD_LEFT + PAD                   # where the text starts, from the left
TEXT_W = CARD_RIGHT - CARD_LEFT - 2 * PAD  # how wide a line of text can get
CENTER = WIDTH // 2
PILL_H = 30
BUTTON_H = 46


def offline_message(reason):
    return f"Couldn't load a verse: {reason}. Press space to try again."


def choose_message():
    reference = random.choice(REFERENCES)
    try:
        verse_text = get_verse(reference)
    except BibleAPIError as error:
        print(f"[WordSelah] {error}", file=sys.stderr)  # the full reason shows in the PyCharm Run window
        saved = [r for r in REFERENCES if is_cached(r)]  # offline: fall back to a verse already downloaded
        if saved:
            reference = random.choice(saved)
            verse_text = get_verse(reference)
        else:
            verse_text = offline_message(error.hint)
    declaration = random.choice(DECLARATIONS[reference]).format(name=USER_NAME)
    return f"{reference} (KJV)", verse_text, declaration


def make_window():
    window = tk.Tk()
    window.title("Scriptures for my heart")
    window.resizable(False, False)
    return window


def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()


def blend(color1, color2, amount):
    r1, g1, b1 = (int(color1[i:i + 2], 16) for i in (1, 3, 5))
    r2, g2, b2 = (int(color2[i:i + 2], 16) for i in (1, 3, 5))
    r = int(r1 + (r2 - r1) * amount)
    g = int(g1 + (g2 - g1) * amount)
    b = int(b1 + (b2 - b1) * amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def draw_gradient(canvas, width, height, top, bottom):
    for y in range(height):
        color = blend(top, bottom, y / height)
        canvas.create_line(0, y, width, y, fill=color)


def rounded_rect(canvas, x1, y1, x2, y2, r, **options):
    points = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
              x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
              x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(points, smooth=True, **options)


def make_text(canvas, text, font, color, anchor="nw", width=TEXT_W):
    justify = "center" if anchor in ("n", "center") else "left"
    return canvas.create_text(0, 0, text=text, font=font, fill=color,
                              anchor=anchor, width=width, justify=justify)


def text_size(canvas, item):
    box = canvas.bbox(item)
    return box[2] - box[0], box[3] - box[1]


def place(canvas, item, x, y):
    canvas.coords(item, x, y)
    canvas.tag_raise(item)


def draw_background(canvas, height):
    draw_gradient(canvas, WIDTH, height, BG_TOP, BG_BOTTOM)
    canvas.create_oval(-70, -70, 70, 70, fill=GOLD_DARK, outline="")
    canvas.create_oval(WIDTH - 70, -70, WIDTH + 70, 70, fill=GOLD_DARK, outline="")


def draw_card(canvas, top, bottom):
    rounded_rect(canvas, CARD_LEFT, top, CARD_RIGHT, bottom, 20, fill=CREAM, outline=GOLD, width=4)


def draw_pill(canvas, y, pill_w):
    rounded_rect(canvas, TEXT_X, y, TEXT_X + pill_w, y + PILL_H, 10, fill=RED, outline="")


def draw_divider(canvas, y):  # the thin gold line between the verse and the declaration
    canvas.create_line(TEXT_X, y, TEXT_X + TEXT_W, y, fill=GOLD_DARK, width=1)

def day_of_year():
    return datetime.date.today().timetuple().tm_yday


def make_stats(canvas, numbers):
    stats = []
    for number, name in zip(numbers, STAT_LABELS):
        number_item = make_text(canvas, str(number), STAT_FONT, INK, anchor="n", width=0)
        label_item = make_text(canvas, name, STAT_LABEL_FONT, MUTED, anchor="n", width=0)
        stats.append((number_item, label_item))
    return stats


def place_stats(canvas, stats, y):
    for i, (number_item, label_item) in enumerate(stats):
        x = TEXT_X + TEXT_W * (2 * i + 1) / 6
        place(canvas, number_item, x, y)
        _, number_h = text_size(canvas, number_item)
        place(canvas, label_item, x, y + number_h + 2)

def hide_window(window):
    window.iconify()


def draw_hide_button(canvas, window, y):  # a gold HIDE button under the card
    x1, x2 = CENTER - 90, CENTER + 90
    rounded_rect(canvas, x1, y, x2, y + BUTTON_H, 12, fill=GOLD, outline="", tags="hide")
    canvas.create_text(CENTER, y + BUTTON_H / 2, text="HIDE", font=BUTTON_FONT,
                       fill=INK, tags="hide")
    canvas.tag_bind("hide", "<Button-1>", lambda event: hide_window(window))


def show_message(window):
    reference, verse_text, declaration = choose_message()
    clear_window(window)
    canvas = tk.Canvas(window, width=WIDTH, height=100, highlightthickness=0)
    canvas.pack()

    # create all the text first
    title = make_text(canvas, "† SCRIPTURE COMPANION †", TITLE_FONT, GOLD, anchor="n", width=0)
    subtitle = make_text(canvas, "A word for your heart, every two hours", SUBTITLE_FONT, GOLD_SOFT, anchor="n", width=0)
    pill_text = make_text(canvas, "COMMIT TO MEMORY", PILL_FONT, "white", anchor="center", width=0)
    ref = make_text(canvas, reference, REF_FONT, REF_COLOR)
    verse = make_text(canvas, verse_text, VERSE_FONT, INK)
    decl_label = make_text(canvas, "MY DECLARATION", LABEL_FONT, MUTED, width=0)
    decl = make_text(canvas, declaration, DECL_FONT, INK)
    footer = make_text(canvas, "Next scripture in 2 hours", FOOTER_FONT, MUTED, width=0)  # placeholder until the timer step
    _, title_h = text_size(canvas, title)
    _, subtitle_h = text_size(canvas, subtitle)
    pill_text_w, _ = text_size(canvas, pill_text)
    _, ref_h = text_size(canvas, ref)
    _, verse_h = text_size(canvas, verse)
    _, label_h = text_size(canvas, decl_label)
    _, decl_h = text_size(canvas, decl)
    _, footer_h = text_size(canvas, footer)
    pill_w = pill_text_w + 36
    read_count = 0  #placeholder until the database step
    saved_count = 0  #placeholder until the bookmark step
    stats = make_stats(canvas, [read_count, saved_count, day_of_year()])
    _, stat_number_h = text_size(canvas, stats[0][0])
    _, stat_label_h = text_size(canvas, stats[0][1])
    stats_h = stat_number_h + 2 + stat_label_h

    # work out where everything goes (the card grows with the text)
    title_y = 28
    subtitle_y = title_y + title_h + 4
    card_top = subtitle_y + subtitle_h + 26
    pill_y = card_top + PAD
    ref_y = pill_y + PILL_H + 22
    verse_y = ref_y + ref_h + 8
    divider_y = verse_y + verse_h + 24
    label_y = divider_y + 22
    decl_y = label_y + label_h + 8
    footer_y = decl_y + decl_h + 24
    stats_divider_y = footer_y + footer_h + 22
    stats_y = stats_divider_y + 20
    card_bottom = stats_y + stats_h + PAD
    button_y = card_bottom + 28
    height = button_y + BUTTON_H + 30
    canvas.config(height=height)

    # draw everything, back to front
    draw_background(canvas, height)
    draw_card(canvas, card_top, card_bottom)
    draw_pill(canvas, pill_y, pill_w)
    draw_divider(canvas, divider_y)
    draw_divider(canvas, stats_divider_y)
    draw_hide_button(canvas, window, button_y)

    # put the words on top
    place(canvas, title, CENTER, title_y)
    place(canvas, subtitle, CENTER, subtitle_y)
    place(canvas, pill_text, TEXT_X + pill_w / 2, pill_y + PILL_H / 2)
    place(canvas, ref, TEXT_X, ref_y)
    place(canvas, verse, TEXT_X, verse_y)
    place(canvas, decl_label, TEXT_X, label_y)
    place(canvas, decl, TEXT_X, decl_y)
    place(canvas, footer, TEXT_X, footer_y)
    place_stats(canvas, stats, stats_y)


def main():  #space bar shows a new message, so pressing Hide doesn't also change it
    window = make_window()
    show_message(window)
    window.bind("<space>", lambda event: show_message(window))  # TEMPORARY test
    window.focus_set()
    window.mainloop()


if __name__ == "__main__":
    main()