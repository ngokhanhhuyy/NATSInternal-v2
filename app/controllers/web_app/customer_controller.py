from flask import *
from sqlalchemy.exc import NoResultFound
from app import application
from app.data import getDatabaseSession
from app.models.customer import Customer
from app.services.customer_service import CustomerService
from app.services.authentication_service import loginRequired
from app.services.authorization_service import permissionRequired
from app.forms import CustomerSearchForm, CustomerSortForm
from app.validators import CustomerSortValidator
from app.errors import NotFoundError
from app.extensions.date_time import Time
from marshmallow import ValidationError
from datetime import datetime
from devtools import debug

@application.route("/customers", endpoint="customerStatistics", methods=["GET"])
@application.route("/customers/", endpoint="customerStatistics", methods=["GET"])
@loginRequired
@permissionRequired("Xem khách hàng")
def customerStatistics():
    totalCounts = CustomerService.getCustomerCountsOverLast4Months()
    newCounts = CustomerService.getNewCustomerCountsOverLast4Months()
    loyalCounts = CustomerService.getLoyalCustomerCountsOverLast4Months()
    highValueCounts = CustomerService.getHighValueCustomerCountsOverLast4Months()
    top5ByOrderAmount = CustomerService.getTop5CustomersByAmountInThisMonth()
    top5ByOrderCount = CustomerService.getTop5CustomersByCountInThisMonth()
    deltaTimeOverLast6Months = CustomerService.getNewCustomerDeltaTimeOverLast6Months()
    return render_template(
        "customer/customer_statistics.html",
        totalCounts=totalCounts,
        newCounts=newCounts,
        loyalCounts=loyalCounts,
        highValueCounts=highValueCounts,
        top5ByOrderAmount=top5ByOrderAmount,
        top5ByOrderCount=top5ByOrderCount,
        deltaTimeOverLast6Months=deltaTimeOverLast6Months)


@application.route("/customers/list", endpoint="customerList", methods=["GET"])
@application.route("/customers/list/", endpoint="customerList", methods=["GET"])
@loginRequired
@permissionRequired("Xem khách hàng")
def customerList():
    # Forms
    searchForm = CustomerSearchForm(meta={"csrf": False})
    sortForm = CustomerSortForm(request.args, meta={"csrf": False})
    if sortForm.validate():
        result = CustomerService.getAllCustomers(
            page=sortForm.page.data,
            sortByField=sortForm.sortByField.data,
            sortOrder=sortForm.sortOrder.data)
    else:
        sortForm = CustomerSortForm(meta={"csrf": False})
        abort(400)
    return render_template(
        "customer/customer_list.html",
        searchForm=searchForm,
        sortForm=sortForm,
        pageCount=result.pageCount if result is not None else 0,
        customers=result.customers if result is not None else None)

@application.route("/customers/search/", endpoint="customerSearch", methods=["GET"])
@application.route("/customers/search", endpoint="customerSearch", methods=["GET"])
@loginRequired
@permissionRequired("Xem khách hàng")
def customerSearch():
    searchForm = CustomerSearchForm(request.args, meta={"csrf": False})
    if searchForm.validate():
        try:
            result = CustomerService.searchForCustomers(
                page=searchForm.page.data,
                field=searchForm.searchField.data,
                content=searchForm.searchContent.data)
        except ValueError:
            abort(400)
    else:
        result = None
        searchForm = CustomerSearchForm(meta={"csrf": False})
    return render_template(
        "customer/customer_search.html",
        searchForm=searchForm,
        pageCount=result.pageCount if result is not None else 0,
        customers=result.customers if result is not None else None)

@application.route("/customers/<int:customerID>", endpoint="customerProfile", methods=["GET"])
@application.route("/customers/<int:customerID>/", endpoint="customerProfile", methods=["GET"])
@loginRequired
@permissionRequired("Xem khách hàng")
def customerPRofile(customerID: int):
    try:
        result = CustomerService.getCustomerByID(customerID=customerID)
    except NoResultFound:
        abort(404)
    return render_template(
        "customer/customer_profile.html",
        customer=result)
