from django.http import HttpResponse, HttpResponseRedirect, Http404
from django import forms
from django.views.generic import ListView, CreateView, UpdateView
from django.template import loader 
from django.shortcuts import render, redirect
from inv_check.models import Item, Coming, Sale, Order
from django.db.models import Max

from .forms import NameForm,ItemSaleForm, addItemForm, orderForm #, ItemSelectForm

def index(request):
   #return HttpResponse("<h1><strong><center>SC Cycling Inventory</center></strong></h1>")
   latestYear = Item.objects.aggregate(Max('year'))['year__max']
   
   # fetch the latest items that are for sale
   latestItems = Item.objects.filter(year=latestYear) | Item.objects.filter(forSale=True)
   
   # create dictionary of fields and values to print
   datDict = {}
   datDict['headers'] =  ['item','gender','available sizes','price']
   datDict['rows'] = []
   countFields = [ 'xxs','xs','s','m','l','xl','xxl','xxxl','count']
   for item in latestItems:
       itemName =  item.item
       sizeList = []
       for size in countFields:
            if getattr(latestItems[0],size)>0:
                sizeList.append(size)
       datDict['rows'].append([itemName.title(),item.gender,",".join(sizeList).upper(),item.retail_price])

   # create context
   context = {'fields':datDict}     
   return render(request, 'inv_check/index.html', context)

class itemsListView(ListView):
    model = Item
    context_object_name = 'item'

## fetch item details using item id    
def fetchItemDetails(item_id, fields2exclude = ['coming', 'sale', 'id','order']):    
    countFields = [ 'xxs','xs','s','m','l','xl','xxl','xxxl','count']
    item = Item.objects.get(pk = item_id)
    
    # get item fields and values into a dictionary
    datDict = {}
    for field in [i.name for i in item._meta.get_fields()]:
        if field not in fields2exclude:
            val = getattr(item, field)
            # filter out 0 value count fields
            if (field in countFields):
                if (val>0):
                    datDict[field.upper()] = val
            else:
                datDict[field.title()] = val
    return(datDict)
    
def fetchOrderDetails(item_id, fields2exclude = ['coming', 'sale', 'id','order']):    
    countFields = [ 'xxs','xs','s','m','l','xl','xxl','xxxl','count']
    item = Order.objects.get(pk = item_id)
    
    # get item fields and values into a dictionary
    datDict = {}
    for field in [i.name for i in item._meta.get_fields()]:
        if field not in fields2exclude:
            val = getattr(item, field)
            datDict[field.title()] = val
    return(datDict)    
    
## these views return search results in same window:
def findbyname(request):
    # if this is a POST request we need to process the form data
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        itemName = request.GET.get('item-name')
        print(itemName)
        if itemName:
            itemsFound = Item.objects.filter(item__icontains=itemName)
            try:
                itemID = itemsFound[0].id
                datDict = fetchItemDetails(itemID)
                keys = datDict.keys()      
                # unpack them into another dictionary for printing table
                fields = {
                    'headers': list(keys),
                    'rows':[datDict[key] for key in keys]}
                context = {'fields':fields}
                return render(request, 'inv_check/detailshow.html', context)    
            except IndexError:
                raise Http404("Item does not exist")
                
    fields = {'headers':[], 'rows':[]}
    context = {'fields':fields}
    return render(request, 'inv_check/detailshow.html', context)      

## Select item functions 
def findBySelection(request):
    items = Item.objects.all()
    # show all items
    itemChoices = Item.objects.all() 
    
    # create initial context
    context = {'itemChoices':itemChoices, 'fields':{'headers':[], 'rows':[]}}
    
    # show request on the website
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        itemName = request.GET.get('item-choice')
        print(itemName)
        if itemName:
            itemsFound = Item.objects.filter(item__icontains=itemName)
            itemID = itemsFound[0].id
            datDict = fetchItemDetails(itemID, )
            keys = datDict.keys()      
            # unpack them into another dictionary for printing table
            fields = {
                'headers': list(keys),
                'rows':[datDict[key] for key in keys]}
            context['fields'] = fields
            return render(request, 'inv_check/itemchoicesshow.html', context)      

    return render(request, 'inv_check/itemchoicesshow.html', context)   

def findBySelectionPublic(request):
    items = Item.objects.all()
    # only show items for sale
    itemChoices = Item.objects.filter(forSale=True) 
    
    # create initial context
    context = {'itemChoices':itemChoices, 'fields':{'headers':[], 'rows':[]}}
    
    # show request on the website
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        itemName = request.GET.get('item-choice')
        print(itemName)
        if itemName:
            itemsFound = Item.objects.filter(item__icontains=itemName)
            itemID = itemsFound[0].id
            datDict = fetchItemDetails(itemID,['coming', 'sale','order','id','forSale','team_price'])
            keys = datDict.keys()      
            # unpack them into another dictionary for printing table
            fields = {
                'headers': list(keys),
                'rows':[datDict[key] for key in keys]}
            context['fields'] = fields
            return render(request, 'inv_check/itemchoicesshow.html', context)      

    return render(request, 'inv_check/itemchoicesshow.html', context) 
    
def recordSale(request):
   context = {'form':ItemSaleForm(),'fields':{'headers':[], 'rows':[]}}
   if request.method == 'POST':
        form = ItemSaleForm(request.POST)
         
        if form.is_valid():
            sale = form.save(commit=False)
            # get corresponding item
            item = Item.objects.get(item__iexact = sale.item.item)
            itemID = item.id
            if sale.size == 'count':
                n = item.count #old quant
                m = sale.quantity #new quant
                item.count = n - m
                item.save(update_fields = ['count'])
            if sale.size != 'count':
                n = getattr(item, sale.size) #old value
                m = n-sale.quantity #new value
                setattr(item,sale.size,m)
                item.save(update_fields=[sale.size])
        context['fields'] = {'headers':['size','old quantity', 'new quantity'],'rows':[sale.item.item,n,m]}
        return render(request, 'inv_check/sale.html', context)     
   return render(request, 'inv_check/sale.html', context)    
 
def addNewItem(request):
   context = {'form':addItemForm(),'fields':{'headers':[], 'rows':[]}}
   if request.method == 'POST':
        form = addItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
        itemID = item.id
        datDict = fetchItemDetails(itemID)
        keys = datDict.keys()      
        # unpack them into another dictionary for printing table
        fields = {
            'headers': list(keys),
            'rows':[datDict[key] for key in keys]}
        context['fields'] = fields       
        return render(request, 'inv_check/newItem.html', context)

   return render(request, 'inv_check/newItem.html', context)
   
## each item has a URL, this directs the user there        
def showInventory(request, item_id):
    try:
        datDict = fetchItemDetails(item_id)           
        keys = datDict.keys()      
        # unpack them into another dictionary for printing table
        fields = {
            'headers': list(keys),
            'rows':[datDict[key] for key in keys]}
        context = {'fields':fields}
        
    except Item.DoesNotExist:
        raise Http404("Item does not exist")
        
    return render(request, 'inv_check/detail.html', context)
    
def makeOrder(request):
    context = {'form':orderForm(),'fields':{'headers':[], 'rows':[]}} 
    if request.method == 'POST':
        form = orderForm(request.POST)
        if form.is_valid():
            item = form.save(commit=True)
            item.save()
            itemID = item.id
            datDict = fetchOrderDetails(itemID,fields2exclude = ['coming', 'sale', 'id','order','date','completed'])
            keys = datDict.keys()      
            # unpack them into another dictionary for printing table
            fields = {
                'headers': list(keys),
                'rows':[datDict[key] for key in keys]}
            context['fields'] = fields       
            return render(request, 'inv_check/makeorder.html', context)

    return render(request, 'inv_check/makeorder.html', context)

def showOrders(request):
    context = {'fields':{'headers':[], 'rows':[]}} 
    orders = Order.objects.filter(completed=False)
    context['orders'] = orders
    # mark selected order as completed
    if request.method == 'GET':
        orderID = request.GET.get("item-order")
        if orderID:
            print(orderID)
            order2complete = Order.objects.get(id=orderID)
            order2complete.completed = True
            order2complete.save(update_fields=['completed'])
    
    # print uncompleted orders
    if orders:
        fields = [s.name for s in orders[0]._meta.get_fields()]
        datDict = {}
        datDict['headers'] =  fields
        datDict['rows'] = []
        for order in orders:
            row = []
            for field in fields:
                row.append(getattr(order,field))
            datDict['rows'].append(row)
    for key in context['fields'].keys():        
        context['fields'][key] = datDict[key]
    return render(request, 'inv_check/showOrders.html', context)    