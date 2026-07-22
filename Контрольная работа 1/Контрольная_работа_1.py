import csv
import math
import statistics

FILE_PATH = "orders_project_01.csv"

# TASK 1. DATA LOADING, CLEANING AND PREPROCESSING

def load_raw_orders(path: str) -> list:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def to_float_or_none(value):
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def clean_orders(raw_orders: list) -> list:
   
    cleaned = []

    n_bad_quantity = 0
    n_bad_price = 0
    n_bad_discount = 0
    n_missing_quantity = 0
    n_missing_discount = 0

    for row in raw_orders:
        quantity_raw = row.get("Quantity", "")
        price_raw = row.get("UnitPrice", "")
        discount_raw = row.get("Discount", "")

        quantity = to_float_or_none(quantity_raw)
        price = to_float_or_none(price_raw)
        discount = to_float_or_none(discount_raw)

        if quantity_raw is not None and quantity_raw.strip() != "" and quantity is None:
            n_bad_quantity += 1
            continue
        if quantity is not None and quantity < 0:
            n_bad_quantity += 1
            continue
        if quantity is None:
            n_missing_quantity += 1  


        if price is None or price <= 0:
            n_bad_price += 1
            continue

        if discount_raw is not None and discount_raw.strip() != "" and discount is None:
            n_bad_discount += 1
            continue
        if discount is not None and (discount < 0 or discount > 0.3):
            n_bad_discount += 1
            continue
        if discount is None:
            n_missing_discount += 1 

        customer_id = row.get("CustomerID", "")
        customer_id = customer_id.strip() if customer_id else ""
        if customer_id == "":
            customer_id = None

        payment_method = (row.get("PaymentMethod") or "").strip().lower()

        cleaned.append({
            "InvoiceNo": row.get("InvoiceNo"),
            "CustomerID": customer_id,
            "Description": row.get("Description"),
            "Quantity": quantity,      
            "UnitPrice": price,
            "Category": row.get("Category"),
            "Discount": discount,     
            "PaymentMethod": payment_method,
        })

    print(f"Rows with invalid Quantity (negative / not a number): {n_bad_quantity}")
    print(f"Rows with invalid UnitPrice (missing or <= 0):        {n_bad_price}")
    print(f"Rows with invalid Discount (out of [0.0, 0.3]):       {n_bad_discount}")
    print(f"Rows kept after cleaning:                              {len(cleaned)}")
    print(f"Missing Quantity values to be filled with 1:           {n_missing_quantity}")
    print(f"Missing Discount values to be filled with 0:           {n_missing_discount}")

    return cleaned


def fill_missing_values(orders: list) -> None:
    for order in orders:
        if order["Quantity"] is None:
            order["Quantity"] = 1.0
        if order["Discount"] is None:
            order["Discount"] = 0.0


def add_order_sum(orders: list) -> None:
    for order in orders:
        order["Sum"] = order["Quantity"] * order["UnitPrice"] * (1 - order["Discount"])


def split_by_customer_id(orders: list):
    with_id = [o for o in orders if o["CustomerID"] is not None]
    without_id = [o for o in orders if o["CustomerID"] is None]
    return with_id, without_id


print("=" * 90)
print("TASK 1 - LOADING, CLEANING AND PREPROCESSING")
print("=" * 90)

raw_orders = load_raw_orders(FILE_PATH)
print("Raw rows loaded:", len(raw_orders))

orders = clean_orders(raw_orders)
fill_missing_values(orders)
add_order_sum(orders)

payment_methods = sorted(set(o["PaymentMethod"] for o in orders))
print("Unique payment methods after normalization:", payment_methods)

orders_with_id, orders_without_id = split_by_customer_id(orders)
print("Orders WITH CustomerID:   ", len(orders_with_id))
print("Orders WITHOUT CustomerID:", len(orders_without_id))
print("Final clean dataset size: ", len(orders))


# TASK 2. DATA ANALYSIS PREPARATION

def group_by_category(orders: list) -> dict:
    result = {}
    for order in orders:
        cat = order["Category"]
        result.setdefault(cat, []).append(order)
    return result


def most_popular_item(orders: list) -> str:
    qty_by_item = {}
    for order in orders:
        item = order["Description"]
        qty_by_item[item] = qty_by_item.get(item, 0) + order["Quantity"]
    return max(qty_by_item, key=qty_by_item.get)


def total_quantity(orders: list) -> int:
    return int(sum(order["Quantity"] for order in orders))


def total_sales(orders: list) -> float:
    return sum(order["Quantity"] * order["UnitPrice"] * (1 - order["Discount"]) for order in orders)


def top_customer(orders: list) -> str:
    identified = [o for o in orders if o.get("CustomerID") is not None]
    best_order = max(identified, key=lambda o: o["Quantity"] * o["UnitPrice"] * (1 - o["Discount"]))
    return best_order["CustomerID"]


def sum_by_category(orders: list) -> dict:
    result = {}
    for order in orders:
        cat = order["Category"]
        amount = order["Quantity"] * order["UnitPrice"] * (1 - order["Discount"])
        result[cat] = result.get(cat, 0) + amount
    return result


def top_category(orders: list) -> str:
    sums = sum_by_category(orders)
    return max(sums, key=sums.get)


def top_categories(orders: list, n: int = 3) -> list:
    sums = sum_by_category(orders)
    return sorted(sums, key=sums.get, reverse=True)[:n]


def payment_stats(orders: list) -> dict:
    result = {}
    for order in orders:
        pm = order["PaymentMethod"]
        result.setdefault(pm, []).append(order)
    return result


def average_discount(orders: list) -> float:
    return sum(order["Discount"] for order in orders) / len(orders)


print("\n" + "=" * 90)
print("TASK 2 - FUNCTION CHECKS")
print("=" * 90)
print("Categories:", list(group_by_category(orders).keys()))
print("Most popular item:", most_popular_item(orders))
print("Total quantity sold:", total_quantity(orders))
print("Total sales (discount included): {:.2f}".format(total_sales(orders)))
print("Customer with the most expensive order (CustomerID):", top_customer(orders))
print("Top category by sales:", top_category(orders))
print("Top-3 categories by sales:", top_categories(orders, 3))
print("Payment methods (keys):", list(payment_stats(orders).keys()))
print("Average discount across all orders: {:.4f}".format(average_discount(orders)))


# TASK 3. STATISTICAL ANALYSIS OF ORDER SUMS 


def quantile(sorted_values: list, q: float) -> float:

    n = len(sorted_values)
    if n == 1:
        return sorted_values[0]
    pos = q * (n - 1)
    lower = math.floor(pos)
    upper = math.ceil(pos)
    if lower == upper:
        return sorted_values[int(pos)]
    frac = pos - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * frac


def skewness(values: list, mean_: float, std_: float) -> float:
    n = len(values)
    if n < 3 or std_ == 0:
        return 0.0
    m3 = sum((x - mean_) ** 3 for x in values) / n
    g1 = m3 / (std_ ** 3)
    return math.sqrt(n * (n - 1)) / (n - 2) * g1


def kurtosis_excess(values: list, mean_: float, std_: float) -> float:
    n = len(values)
    if n < 4 or std_ == 0:
        return 0.0
    m4 = sum((x - mean_) ** 4 for x in values) / n
    g2 = m4 / (std_ ** 4) - 3
    return g2


def describe_sums(sums: list, label: str = "") -> dict:
    n = len(sums)
    mean_ = statistics.mean(sums)
    median_ = statistics.median(sums)
    std_ = statistics.stdev(sums) if n > 1 else 0.0 

    sorted_sums = sorted(sums)
    q1 = quantile(sorted_sums, 0.25)
    q3 = quantile(sorted_sums, 0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = [x for x in sums if x < lower_bound or x > upper_bound]

    skew = skewness(sums, mean_, std_)
    kurt = kurtosis_excess(sums, mean_, std_)
    is_normal = abs(skew) < 0.5 and abs(kurt) < 1

    result = {
        "n": n,
        "mean": mean_,
        "median": median_,
        "std": std_,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "outliers": outliers,
        "skewness": skew,
        "kurtosis": kurt,
        "is_normal": is_normal,
    }

    if label:
        print(f"\n--- Order sum statistics: {label} (n={n}) ---")
        print(f"Mean               : {mean_:.2f}")
        print(f"Median             : {median_:.2f}")
        print(f"Std deviation      : {std_:.2f}")
        print(f"Q1 (25th pct)      : {q1:.2f}")
        print(f"Q3 (75th pct)      : {q3:.2f}")
        print(f"IQR                : {iqr:.2f}")
        print(f"Normal range       : [{lower_bound:.2f}, {upper_bound:.2f}]")
        print(f"Number of outliers : {len(outliers)}")
        print(f"Skewness           : {skew:.3f}")
        print(f"Excess kurtosis    : {kurt:.3f}")
        print("Distribution       :", "looks approximately normal" if is_normal else "is NOT normal (skewed / heavy-tailed)")

    return result


all_sums = [o["Sum"] for o in orders]

print("\n" + "=" * 90)
print("TASK 3 - STATISTICS FOR ALL ORDERS (items 1-6)")
print("=" * 90)
overall_stats = describe_sums(all_sums, label="ALL ORDERS")

outliers_list = [
    o for o in orders
    if o["Sum"] < overall_stats["lower_bound"] or o["Sum"] > overall_stats["upper_bound"]
]
print(f"\nOutlier orders stored in a separate list: {len(outliers_list)} orders")
print("First 5 outliers:")
for o in outliers_list[:5]:
    print(f"  {o['InvoiceNo']:<12} {o['Category']:<12} qty={o['Quantity']:<6} "
          f"price={o['UnitPrice']:<8} discount={o['Discount']:<5} sum={o['Sum']:.2f}")


print("\n" + "=" * 90)
print("TASK 3 - STATISTICS PER CATEGORY (item 7)")
print("=" * 90)
by_category = group_by_category(orders)
category_stats = {}
for cat, cat_orders in by_category.items():
    cat_sums = [o["Sum"] for o in cat_orders]
    category_stats[cat] = describe_sums(cat_sums, label=f"Category: {cat}")


print("\n" + "=" * 90)
print("TASK 3 - item 8: FEW LARGE ORDERS vs MANY SMALL ORDERS - WHICH IS MORE PROFITABLE?")
print("=" * 90)
median_sum = overall_stats["median"]
big_orders = [o for o in orders if o["Sum"] >= median_sum]
small_orders = [o for o in orders if o["Sum"] < median_sum]

big_total = sum(o["Sum"] for o in big_orders)
small_total = sum(o["Sum"] for o in small_orders)

print(f"Median order sum: {median_sum:.2f}")
print(f"Large orders (>= median): {len(big_orders)} orders, total {big_total:.2f}, "
      f"average order {big_total / len(big_orders):.2f}")
print(f"Small orders (< median):  {len(small_orders)} orders, total {small_total:.2f}, "
      f"average order {small_total / len(small_orders):.2f}")

if big_total > small_total:
    print("Conclusion: a small number of large orders bring in more total revenue.")
else:
    print("Conclusion: a large number of small orders bring in more total revenue.")


print("\n" + "=" * 90)
print("TASK 3 - item 9: WHICH CATEGORY GIVES THE MAXIMUM SALES?")
print("=" * 90)
sums_by_cat = sum_by_category(orders)
for cat, total in sorted(sums_by_cat.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cat:<15} {total:,.2f}")
best_cat = max(sums_by_cat, key=sums_by_cat.get)
print(f"\nTop category by total sales: {best_cat} ({sums_by_cat[best_cat]:,.2f})")


print("\n" + "=" * 90)
print("TASK 3 - item 10: MOST POPULAR ITEM")
print("=" * 90)
qty_by_item = {}
for o in orders:
    qty_by_item[o["Description"]] = qty_by_item.get(o["Description"], 0) + o["Quantity"]
for item, qty in sorted(qty_by_item.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {item:<20} {qty:.0f}")
best_item = max(qty_by_item, key=qty_by_item.get)
print(f"\nMost popular item: {best_item} ({qty_by_item[best_item]:.0f} units)")


print("\n" + "=" * 90)
print("TASK 3 - items 11-12: IDENTIFIED vs UNIDENTIFIED CUSTOMER ORDERS")
print("=" * 90)
sums_with_id = [o["Sum"] for o in orders_with_id]
sums_without_id = [o["Sum"] for o in orders_without_id]

stats_with_id = describe_sums(sums_with_id, label="Orders WITH CustomerID")
stats_without_id = describe_sums(sums_without_id, label="Orders WITHOUT CustomerID")

mean_diff = stats_with_id["mean"] - stats_without_id["mean"]
print(f"\nDifference in average order sum (with ID - without ID): {mean_diff:.2f}")

def welch_ttest(sample1: list, sample2: list):
    n1, n2 = len(sample1), len(sample2)
    mean1, mean2 = statistics.mean(sample1), statistics.mean(sample2)
    var1, var2 = statistics.variance(sample1), statistics.variance(sample2)

    se = math.sqrt(var1 / n1 + var2 / n2)
    if se == 0:
        return 0.0, None
    t_stat = (mean1 - mean2) / se

    df = (var1 / n1 + var2 / n2) ** 2 / (
        (var1 ** 2) / (n1 ** 2 * (n1 - 1)) + (var2 ** 2) / (n2 ** 2 * (n2 - 1))
    )
    return t_stat, df


t_stat, df = welch_ttest(sums_with_id, sums_without_id)
print(f"Welch's t-test: t = {t_stat:.3f}, df = {df:.1f}")
print("Rule of thumb: with this many degrees of freedom, |t| > ~1.96 roughly "
      "corresponds to a significant difference at the 5% level.")
if abs(t_stat) > 1.96:
    print("=> The difference in average order sum between the two groups looks statistically significant.")
else:
    print("=> No statistically significant difference in average order sum was found between the two groups.")


print("\n" + "=" * 90)
print("TASK 3 - item 13: DOES A DISCOUNT ATTRACT MORE ORDERS / LARGER QUANTITIES?")
print("=" * 90)
no_discount = [o for o in orders if o["Discount"] == 0]
with_discount = [o for o in orders if o["Discount"] > 0]

avg_qty_no_discount = sum(o["Quantity"] for o in no_discount) / len(no_discount) if no_discount else 0
avg_qty_with_discount = sum(o["Quantity"] for o in with_discount) / len(with_discount) if with_discount else 0

print(f"Orders WITHOUT discount: {len(no_discount)}, average Quantity = {avg_qty_no_discount:.2f}")
print(f"Orders WITH discount:    {len(with_discount)}, average Quantity = {avg_qty_with_discount:.2f}")

def pearson_corr(xs: list, ys: list) -> float:
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    std_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    std_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if std_x == 0 or std_y == 0:
        return 0.0
    return cov / (std_x * std_y)


discount_values = [o["Discount"] for o in orders]
quantity_values = [o["Quantity"] for o in orders]
corr_discount_qty = pearson_corr(discount_values, quantity_values)
print(f"Correlation between Discount and Quantity: {corr_discount_qty:.3f}")

t_stat2, df2 = welch_ttest(
    [o["Quantity"] for o in with_discount],
    [o["Quantity"] for o in no_discount],
)
print(f"Welch's t-test (Quantity: discount vs no discount): t = {t_stat2:.3f}, df = {df2:.1f}")

if abs(corr_discount_qty) < 0.1 and abs(t_stat2) < 1.96:
    print("Conclusion: no meaningful relationship was found between discount and purchase volume.")
else:
    print("Conclusion: there does appear to be a relationship between discount and purchase volume.")

