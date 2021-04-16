# Misc note

## Trading Stats
### 15/16 April
#### Ship 1
**Total:** 232080
**Time:** 8:03:40
**Profit per Hour:** 28789.54

#### Ship 2
**Total:** 232370
**Time:** 8:03:01
**Profit per Hour:** 28863.88

## Basic Functionality and Throttle Cost
- Trader: minimum 5 calls to with 3 in close proxmity - currently 15 with 13 in close proximity
- Tracker: minimum 11 calls

## Fuel
**Distance Formula:** $\sqrt{(x_{2} - x_{1})^2 + (y_{2} - y_{1})^2}$
```python 
lambda from_x, from_y, to_x, to_y: round(math.sqrt(math.pow((to_x - from_x),2) + math.pow((to_y - from_y),2)))
  ```

**Fuel Estimator Equation:**
*This is definately not exact however, for the Jacksaw and Graveder it provides accurate results*
- d = distance <br>
$(\frac{9}{37}) \times d + 2$

```python
lambda d: (9/37) * d + 2
```

### Tritus
- Tritus (OE-PM-TR) -> Prime (OE-PM) : 2 Fuel *(for Grav)*
- Tritus (OE-PM-TR) -> Carth (OE-CR) : 13 Fuel *(for Jack)*
- Tritus (OE-PM-TR) -> Nyon (OE-NY) : 24 Fuel *(for Jack)*
- Tritus (OE-PM-TR) -> Koria (OE-KO) : 20 Fuel : 207 Seconds : distance 74 *(for Jack)*
- Tritus (OE-PM-TR) -> Ado (OE-UC-AD) : 39 Fuel : 363 Seconds : distance 152 *(for Jack)*
- Tritus (OE-PM-TR) -> Obo (OE-UC-OB) : 38 Fuel : 351 Seconds : distance 146 *(for Jack)*
- Tritus (OE-PM-TR) -> Ucarro (OE-UC) : 38 Fuel : ? Seconds : distance 147 *(for Jack)*
- Tritus (OE-PM-TR) -> BO (OE-BO) : 28 Fuel : 271 Seconds : distance 106 *(for Jack)*

### Prime
- Prime (OE-PM) -> Tritus (OE-PM-TR) : 4 Fuel *(for Grav)*
- Prime (OE-PM) -> Nyon (OE-NY) : 26 Fuel : 243 Seconds : distance 92 *(for Grav)*

### Nyon
- Nyon (OE-NY) -> Ado (OE-UC-AD) : 41 Fuel : ? Seconds : ? distance *(for Grav)*

### Carth
- Carth (OE-CR) -> Prime (OE-PM) : 14 Fuel : ? Seconds : distance ? *(for Grav)*

### Ucarras
- Ucarras (CE-UC) -> BO (OE-BO) : 47 Fuel : ? Seconds : distance 171 *(for Grav 2)*

