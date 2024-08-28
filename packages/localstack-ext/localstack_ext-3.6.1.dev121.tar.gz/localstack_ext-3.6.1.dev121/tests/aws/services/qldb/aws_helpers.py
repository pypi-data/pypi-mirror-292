# Python functions copied verbatim from the Python driver tutorial
#
# https://docs.aws.amazon.com/qldb/latest/developerguide/getting-started.python.tutorial.html
from array import array
from base64 import b64encode
from datetime import datetime, timedelta
from decimal import Decimal
from functools import reduce
from hashlib import sha256
from logging import INFO, basicConfig, getLogger
from random import randrange

from amazon.ion.simple_types import (
    IonPyBool,
    IonPyBytes,
    IonPyDecimal,
    IonPyDict,
    IonPyFloat,
    IonPyInt,
    IonPyList,
    IonPyNull,
    IonPySymbol,
    IonPyText,
    IonPyTimestamp,
)
from amazon.ion.simpleion import dumps, loads

logger = getLogger(__name__)
basicConfig(level=INFO)

IonValue = (
    IonPyBool,
    IonPyBytes,
    IonPyDecimal,
    IonPyDict,
    IonPyFloat,
    IonPyInt,
    IonPyList,
    IonPyNull,
    IonPySymbol,
    IonPyText,
    IonPyTimestamp,
)


class Constants:
    """
    Constant values used throughout this tutorial.
    """

    LEDGER_NAME = "vehicle-registration"

    VEHICLE_REGISTRATION_TABLE_NAME = "VehicleRegistration"
    VEHICLE_TABLE_NAME = "Vehicle"
    PERSON_TABLE_NAME = "Person"
    DRIVERS_LICENSE_TABLE_NAME = "DriversLicense"

    LICENSE_NUMBER_INDEX_NAME = "LicenseNumber"
    GOV_ID_INDEX_NAME = "GovId"
    VEHICLE_VIN_INDEX_NAME = "VIN"
    LICENSE_PLATE_NUMBER_INDEX_NAME = "LicensePlateNumber"
    PERSON_ID_INDEX_NAME = "PersonId"

    JOURNAL_EXPORT_S3_BUCKET_NAME_PREFIX = "qldb-tutorial-journal-export"
    USER_TABLES = "information_schema.user_tables"
    S3_BUCKET_ARN_TEMPLATE = "arn:aws:s3:::"
    LEDGER_NAME_WITH_TAGS = "tags"

    RETRY_LIMIT = 4


def create_table(driver, table_name):
    """
    Create a table with the specified name.

    :type driver: :py:class:`pyqldb.driver.qldb_driver.QldbDriver`
    :param driver: An instance of the QldbDriver class.

    :type table_name: str
    :param table_name: Name of the table to create.

    :rtype: int
    :return: The number of changes to the database.
    """
    logger.info("Creating the '{}' table...".format(table_name))
    statement = "CREATE TABLE {}".format(table_name)
    cursor = driver.execute_lambda(lambda executor: executor.execute_statement(statement))
    logger.info("{} table created successfully.".format(table_name))
    return len(list(cursor))


def create_index(driver, table_name, index_attribute):
    """
    Create an index for a particular table.

    :type driver: :py:class:`pyqldb.driver.qldb_driver.QldbDriver`
    :param driver: An instance of the QldbDriver class.

    :type table_name: str
    :param table_name: Name of the table to add indexes for.

    :type index_attribute: str
    :param index_attribute: Index to create on a single attribute.

    :rtype: int
    :return: The number of changes to the database.
    """
    logger.info("Creating index on '{}'...".format(index_attribute))
    statement = "CREATE INDEX on {} ({})".format(table_name, index_attribute)
    cursor = driver.execute_lambda(lambda executor: executor.execute_statement(statement))
    return len(list(cursor))


class SampleData:
    """
    Sample domain objects for use throughout this tutorial.
    """

    DRIVERS_LICENSE = [
        {
            "PersonId": "",
            "LicenseNumber": "LEWISR261LL",
            "LicenseType": "Learner",
            "ValidFromDate": datetime(2016, 12, 20),
            "ValidToDate": datetime(2020, 11, 15),
        },
        {
            "PersonId": "",
            "LicenseNumber": "LOGANB486CG",
            "LicenseType": "Probationary",
            "ValidFromDate": datetime(2016, 4, 6),
            "ValidToDate": datetime(2020, 11, 15),
        },
        {
            "PersonId": "",
            "LicenseNumber": "744 849 301",
            "LicenseType": "Full",
            "ValidFromDate": datetime(2017, 12, 6),
            "ValidToDate": datetime(2022, 10, 15),
        },
        {
            "PersonId": "",
            "LicenseNumber": "P626-168-229-765",
            "LicenseType": "Learner",
            "ValidFromDate": datetime(2017, 8, 16),
            "ValidToDate": datetime(2021, 11, 15),
        },
        {
            "PersonId": "",
            "LicenseNumber": "S152-780-97-415-0",
            "LicenseType": "Probationary",
            "ValidFromDate": datetime(2015, 8, 15),
            "ValidToDate": datetime(2021, 8, 21),
        },
    ]
    PERSON = [
        {
            "FirstName": "Raul",
            "LastName": "Lewis",
            "Address": "1719 University Street, Seattle, WA, 98109",
            "DOB": datetime(1963, 8, 19),
            "GovId": "LEWISR261LL",
            "GovIdType": "Driver License",
        },
        {
            "FirstName": "Brent",
            "LastName": "Logan",
            "DOB": datetime(1967, 7, 3),
            "Address": "43 Stockert Hollow Road, Everett, WA, 98203",
            "GovId": "LOGANB486CG",
            "GovIdType": "Driver License",
        },
        {
            "FirstName": "Alexis",
            "LastName": "Pena",
            "DOB": datetime(1974, 2, 10),
            "Address": "4058 Melrose Street, Spokane Valley, WA, 99206",
            "GovId": "744 849 301",
            "GovIdType": "SSN",
        },
        {
            "FirstName": "Melvin",
            "LastName": "Parker",
            "DOB": datetime(1976, 5, 22),
            "Address": "4362 Ryder Avenue, Seattle, WA, 98101",
            "GovId": "P626-168-229-765",
            "GovIdType": "Passport",
        },
        {
            "FirstName": "Salvatore",
            "LastName": "Spencer",
            "DOB": datetime(1997, 11, 15),
            "Address": "4450 Honeysuckle Lane, Seattle, WA, 98101",
            "GovId": "S152-780-97-415-0",
            "GovIdType": "Passport",
        },
    ]
    VEHICLE = [
        {
            "VIN": "1N4AL11D75C109151",
            "Type": "Sedan",
            "Year": 2011,
            "Make": "Audi",
            "Model": "A5",
            "Color": "Silver",
        },
        {
            "VIN": "KM8SRDHF6EU074761",
            "Type": "Sedan",
            "Year": 2015,
            "Make": "Tesla",
            "Model": "Model S",
            "Color": "Blue",
        },
        {
            "VIN": "3HGGK5G53FM761765",
            "Type": "Motorcycle",
            "Year": 2011,
            "Make": "Ducati",
            "Model": "Monster 1200",
            "Color": "Yellow",
        },
        {
            "VIN": "1HVBBAANXWH544237",
            "Type": "Semi",
            "Year": 2009,
            "Make": "Ford",
            "Model": "F 150",
            "Color": "Black",
        },
        {
            "VIN": "1C4RJFAG0FC625797",
            "Type": "Sedan",
            "Year": 2019,
            "Make": "Mercedes",
            "Model": "CLK 350",
            "Color": "White",
        },
    ]
    VEHICLE_REGISTRATION = [
        {
            "VIN": "1N4AL11D75C109151",
            "LicensePlateNumber": "LEWISR261LL",
            "State": "WA",
            "City": "Seattle",
            "ValidFromDate": datetime(2017, 8, 21),
            "ValidToDate": datetime(2020, 5, 11),
            "PendingPenaltyTicketAmount": Decimal("90.25"),
            "Owners": {"PrimaryOwner": {"PersonId": ""}, "SecondaryOwners": []},
        },
        {
            "VIN": "KM8SRDHF6EU074761",
            "LicensePlateNumber": "CA762X",
            "State": "WA",
            "City": "Kent",
            "PendingPenaltyTicketAmount": Decimal("130.75"),
            "ValidFromDate": datetime(2017, 9, 14),
            "ValidToDate": datetime(2020, 6, 25),
            "Owners": {"PrimaryOwner": {"PersonId": ""}, "SecondaryOwners": []},
        },
        {
            "VIN": "3HGGK5G53FM761765",
            "LicensePlateNumber": "CD820Z",
            "State": "WA",
            "City": "Everett",
            "PendingPenaltyTicketAmount": Decimal("442.30"),
            "ValidFromDate": datetime(2011, 3, 17),
            "ValidToDate": datetime(2021, 3, 24),
            "Owners": {"PrimaryOwner": {"PersonId": ""}, "SecondaryOwners": []},
        },
        {
            "VIN": "1HVBBAANXWH544237",
            "LicensePlateNumber": "LS477D",
            "State": "WA",
            "City": "Tacoma",
            "PendingPenaltyTicketAmount": Decimal("42.20"),
            "ValidFromDate": datetime(2011, 10, 26),
            "ValidToDate": datetime(2023, 9, 25),
            "Owners": {"PrimaryOwner": {"PersonId": ""}, "SecondaryOwners": []},
        },
        {
            "VIN": "1C4RJFAG0FC625797",
            "LicensePlateNumber": "TH393F",
            "State": "WA",
            "City": "Olympia",
            "PendingPenaltyTicketAmount": Decimal("30.45"),
            "ValidFromDate": datetime(2013, 9, 2),
            "ValidToDate": datetime(2024, 3, 19),
            "Owners": {"PrimaryOwner": {"PersonId": ""}, "SecondaryOwners": []},
        },
    ]


def convert_object_to_ion(py_object):
    """
    Convert a Python object into an Ion object.

    :type py_object: object
    :param py_object: The object to convert.

    :rtype: :py:class:`amazon.ion.simple_types.IonPyValue`
    :return: The converted Ion object.
    """
    ion_object = loads(dumps(py_object))
    return ion_object


def to_ion_struct(key, value):
    """
    Convert the given key and value into an Ion struct.

    :type key: str
    :param key: The key which serves as an unique identifier.

    :type value: str
    :param value: The value associated with a given key.

    :rtype: :py:class:`amazon.ion.simple_types.IonPyDict`
    :return: The Ion dictionary object.
    """
    ion_struct = dict()
    ion_struct[key] = value
    return loads(str(ion_struct))


def get_document_ids(transaction_executor, table_name, field, value):
    """
    Gets the document IDs from the given table.

    :type transaction_executor: :py:class:`pyqldb.execution.executor.Executor`
    :param transaction_executor: An Executor object allowing for execution of statements within a transaction.

    :type table_name: str
    :param table_name: The table name to query.

    :type field: str
    :param field: A field to query.

    :type value: str
    :param value: The key of the given field.

    :rtype: list
    :return: A list of document IDs.
    """
    query = "SELECT id FROM {} AS t BY id WHERE t.{} = ?".format(table_name, field)
    cursor = transaction_executor.execute_statement(query, convert_object_to_ion(value))
    return list(map(lambda table: table.get("id"), cursor))


def get_document_ids_from_dml_results(result):
    """
    Return a list of modified document IDs as strings from DML results.

    :type result: :py:class:`pyqldb.cursor.buffered_cursor.BufferedCursor`
    :param: result: The result set from DML operation.

    :rtype: list
    :return: List of document IDs.
    """
    ret_val = list(map(lambda x: x.get("documentId"), result))
    return ret_val


def print_result(cursor):
    """
    Pretty print the result set. Returns the number of documents in the result set.

    :type cursor: :py:class:`pyqldb.cursor.stream_cursor.StreamCursor`/
                  :py:class:`pyqldb.cursor.buffered_cursor.BufferedCursor`
    :param cursor: An instance of the StreamCursor or BufferedCursor class.

    :rtype: int
    :return: Number of documents in the result set.
    """
    result_counter = 0
    for row in cursor:
        # Each row would be in Ion format.
        print_ion(row)
        result_counter += 1
    return result_counter


def print_ion(ion_value):
    """
    Pretty print an Ion Value.

    :type ion_value: :py:class:`amazon.ion.simple_types.IonPySymbol`
    :param ion_value: Any Ion Value to be pretty printed.
    """
    logger.info(dumps(ion_value, binary=False, indent="  ", omit_version_marker=True))


def update_person_id(document_ids):
    """
    Update the PersonId value for DriversLicense records and the PrimaryOwner value for VehicleRegistration records.

    :type document_ids: list
    :param document_ids: List of document IDs.

    :rtype: list
    :return: Lists of updated DriversLicense records and updated VehicleRegistration records.
    """
    new_drivers_licenses = SampleData.DRIVERS_LICENSE.copy()
    new_vehicle_registrations = SampleData.VEHICLE_REGISTRATION.copy()
    for i in range(len(SampleData.PERSON)):
        drivers_license = new_drivers_licenses[i]
        registration = new_vehicle_registrations[i]
        drivers_license.update({"PersonId": str(document_ids[i])})
        registration["Owners"]["PrimaryOwner"].update({"PersonId": str(document_ids[i])})
    return new_drivers_licenses, new_vehicle_registrations


def insert_documents(driver, table_name, documents):
    """
    Insert the given list of documents into a table in a single transaction.

    :type driver: :py:class:`pyqldb.driver.qldb_driver.QldbDriver`
    :param driver: An instance of the QldbDriver class.

    :type table_name: str
    :param table_name: Name of the table to insert documents into.

    :type documents: list
    :param documents: List of documents to insert.

    :rtype: list
    :return: List of documents IDs for the newly inserted documents.
    """
    logger.info("Inserting some documents in the {} table...".format(table_name))
    statement = "INSERT INTO {} ?".format(table_name)
    cursor = driver.execute_lambda(
        lambda executor: executor.execute_statement(statement, convert_object_to_ion(documents))
    )
    list_of_document_ids = get_document_ids_from_dml_results(cursor)

    return list_of_document_ids


def update_and_insert_documents(driver):
    """
    Handle the insertion of documents and updating PersonIds.

    :type driver: :py:class:`pyqldb.driver.qldb_driver.QldbDriver`
    :param driver: An instance of the QldbDriver class.
    """
    list_ids = insert_documents(driver, Constants.PERSON_TABLE_NAME, SampleData.PERSON)

    logger.info(
        "Updating PersonIds for 'DriversLicense' and PrimaryOwner for 'VehicleRegistration'..."
    )
    new_licenses, new_registrations = update_person_id(list_ids)

    insert_documents(driver, Constants.VEHICLE_TABLE_NAME, SampleData.VEHICLE)
    insert_documents(driver, Constants.VEHICLE_REGISTRATION_TABLE_NAME, new_registrations)
    insert_documents(driver, Constants.DRIVERS_LICENSE_TABLE_NAME, new_licenses)


def find_person_from_document_id(transaction_executor, document_id):
    """
    Query a driver's information using the given ID.

    :type transaction_executor: :py:class:`pyqldb.execution.executor.Executor`
    :param transaction_executor: An Executor object allowing for execution of statements within a transaction.

    :type document_id: :py:class:`amazon.ion.simple_types.IonPyText`
    :param document_id: The document ID required to query for the person.

    :rtype: :py:class:`amazon.ion.simple_types.IonPyDict`
    :return: The resulting document from the query.
    """
    query = "SELECT p.* FROM Person AS p BY pid WHERE pid = ?"
    cursor = transaction_executor.execute_statement(query, document_id)
    return next(cursor)


def find_primary_owner_for_vehicle(driver, vin):
    """
    Find the primary owner of a vehicle given its VIN.

    :type driver: :py:class:`pyqldb.driver.qldb_driver.QldbDriver`
    :param driver: An instance of the QldbDriver class.

    :type vin: str
    :param vin: The VIN to find primary owner for.

    :rtype: :py:class:`amazon.ion.simple_types.IonPyDict`
    :return: The resulting document from the query.
    """
    logger.info("Finding primary owner for vehicle with VIN: {}.".format(vin))
    query = "SELECT Owners.PrimaryOwner.PersonId FROM VehicleRegistration AS v WHERE v.VIN = ?"
    cursor = driver.execute_lambda(
        lambda executor: executor.execute_statement(query, convert_object_to_ion(vin))
    )
    try:
        return driver.execute_lambda(
            lambda executor: find_person_from_document_id(executor, next(cursor).get("PersonId"))
        )
    except StopIteration:
        logger.error("No primary owner registered for this vehicle.")
        return None


def update_vehicle_registration(driver, vin, document_id):
    """
    Update the primary owner for a vehicle using the given VIN.

    :type driver: :py:class:`pyqldb.driver.qldb_driver.QldbDriver`
    :param driver: An instance of the QldbDriver class.

    :type vin: str
    :param vin: The VIN for the vehicle to operate on.

    :type document_id: :py:class:`amazon.ion.simple_types.IonPyText`
    :param document_id: New PersonId for the primary owner.

    :raises RuntimeError: If no vehicle registration was found using the given document ID and VIN.
    """
    logger.info("Updating the primary owner for vehicle with Vin: {}...".format(vin))
    statement = (
        "UPDATE VehicleRegistration AS r SET r.Owners.PrimaryOwner.PersonId = ? WHERE r.VIN = ?"
    )
    cursor = driver.execute_lambda(
        lambda executor: executor.execute_statement(
            statement, document_id, convert_object_to_ion(vin)
        )
    )
    try:
        print_result(cursor)
        logger.info("Successfully transferred vehicle with VIN: {} to new owner.".format(vin))
    except StopIteration:
        raise RuntimeError("Unable to transfer vehicle, could not find registration.")


def validate_and_update_registration(driver, vin, current_owner, new_owner):
    """
    Validate the current owner of the given vehicle and transfer its ownership to a new owner.

    :type driver: :py:class:`pyqldb.driver.qldb_driver.QldbDriver`
    :param driver: An instance of the QldbDriver class.

    :type vin: str
    :param vin: The VIN of the vehicle to transfer ownership of.

    :type current_owner: str
    :param current_owner: The GovId of the current owner of the vehicle.

    :type new_owner: str
    :param new_owner: The GovId of the new owner of the vehicle.

    :raises RuntimeError: If unable to verify primary owner.
    """
    primary_owner = find_primary_owner_for_vehicle(driver, vin)
    if primary_owner is None or primary_owner["GovId"] != current_owner:
        raise RuntimeError("Incorrect primary owner identified for vehicle, unable to transfer.")

    document_ids = driver.execute_lambda(
        lambda executor: get_document_ids(executor, Constants.PERSON_TABLE_NAME, "GovId", new_owner)
    )
    update_vehicle_registration(driver, vin, document_ids[0])


def format_date_time(date_time):
    """
    Format the given date time to a string.

    :type date_time: :py:class:`datetime.datetime`
    :param date_time: The date time to format.

    :rtype: str
    :return: The formatted date time.
    """
    return date_time.strftime("`%Y-%m-%dT%H:%M:%S.%fZ`")


def previous_primary_owners(driver, vin):
    """
    Find previous primary owners for the given VIN in a single transaction.
    In this example, query the `VehicleRegistration` history table to find all previous primary owners for a VIN.

    :type driver: :py:class:`pyqldb.driver.qldb_driver.QldbDriver`
    :param driver: An instance of the QldbDriver class.

    :type vin: str
    :param vin: VIN to find previous primary owners for.
    """
    person_ids = driver.execute_lambda(
        lambda executor: get_document_ids(
            executor, Constants.VEHICLE_REGISTRATION_TABLE_NAME, "VIN", vin
        )
    )

    todays_date = datetime.utcnow() - timedelta(seconds=1)
    three_months_ago = todays_date - timedelta(days=90)
    query = "SELECT data.Owners.PrimaryOwner, metadata.version FROM history({}, {}, {}) AS h WHERE h.metadata.id = ?".format(
        Constants.VEHICLE_REGISTRATION_TABLE_NAME,
        format_date_time(three_months_ago),
        format_date_time(todays_date),
    )

    for ids in person_ids:
        logger.info("Querying the 'VehicleRegistration' table's history using VIN: {}.".format(vin))
        cursor = driver.execute_lambda(lambda executor: executor.execute_statement(query, ids))
        # Deviation from AWS documentation
        yield list(cursor)
        # if not (print_result(cursor)) > 0:
        #     logger.info(
        #         "No modification history found within the given time frame for document ID: {}".format(
        #             ids
        #         )
        #     )


def block_address_to_dictionary(ion_dict):
    """
    Convert a block address from IonPyDict into a dictionary.
    Shape of the dictionary must be: {'IonText': "{strandId: <"strandId">, sequenceNo: <sequenceNo>}"}

    :type ion_dict: :py:class:`amazon.ion.simple_types.IonPyDict`/str
    :param ion_dict: The block address value to convert.

    :rtype: dict
    :return: The converted dict.
    """
    block_address = {"IonText": {}}
    if not isinstance(ion_dict, str):
        py_dict = '{{strandId: "{}", sequenceNo:{}}}'.format(
            ion_dict["strandId"], ion_dict["sequenceNo"]
        )
        ion_dict = py_dict
    block_address["IonText"] = ion_dict
    return block_address


HASH_LENGTH = 32
UPPER_BOUND = 8


def parse_proof(value_holder):
    """
    Parse the Proof object returned by QLDB into an iterator.

    The Proof object returned by QLDB is a dictionary like the following:
    {'IonText': '[{{<hash>}},{{<hash>}}]'}

    :type value_holder: dict
    :param value_holder: A structure containing an Ion string value.

    :rtype: :py:class:`amazon.ion.simple_types.IonPyList`
    :return: A list of hash values.
    """
    value_holder = value_holder.get("IonText")
    proof_list = loads(value_holder)
    return proof_list


def parse_block(value_holder):
    """
    Parse the Block object returned by QLDB and retrieve block hash.

    :type value_holder: dict
    :param value_holder: A structure containing an Ion string value.

    :rtype: :py:class:`amazon.ion.simple_types.IonPyBytes`
    :return: The block hash.
    """
    value_holder = value_holder.get("IonText")
    block = loads(value_holder)
    block_hash = block.get("blockHash")
    return block_hash


def flip_random_bit(original):
    """
    Flip a single random bit in the given hash value.
    This method is used to demonstrate QLDB's verification features.

    :type original: bytes
    :param original: The hash value to alter.

    :rtype: bytes
    :return: The altered hash with a single random bit changed.
    """
    assert len(original) != 0, "Invalid bytes."

    altered_position = randrange(len(original))
    bit_shift = randrange(UPPER_BOUND)
    altered_hash = bytearray(original).copy()

    altered_hash[altered_position] = altered_hash[altered_position] ^ (1 << bit_shift)
    return bytes(altered_hash)


def compare_hash_values(hash1, hash2):
    """
    Compare two hash values by converting them into byte arrays, assuming they are little endian.

    :type hash1: bytes
    :param hash1: The hash value to compare.

    :type hash2: bytes
    :param hash2: The hash value to compare.

    :rtype: int
    :return: Zero if the hash values are equal, otherwise return the difference of the first pair of non-matching bytes.
    """
    assert len(hash1) == HASH_LENGTH
    assert len(hash2) == HASH_LENGTH

    hash_array1 = array("b", hash1)
    hash_array2 = array("b", hash2)

    for i in range(len(hash_array1) - 1, -1, -1):
        difference = hash_array1[i] - hash_array2[i]
        if difference != 0:
            return difference
    return 0


def join_hash_pairwise(hash1, hash2):
    """
    Take two hash values, sort them, concatenate them, and generate a new hash value from the concatenated values.

    :type hash1: bytes
    :param hash1: Hash value to concatenate.

    :type hash2: bytes
    :param hash2: Hash value to concatenate.

    :rtype: bytes
    :return: The new hash value generated from concatenated hash values.
    """
    if len(hash1) == 0:
        return hash2
    if len(hash2) == 0:
        return hash1

    concatenated = hash1 + hash2 if compare_hash_values(hash1, hash2) < 0 else hash2 + hash1
    new_hash_lib = sha256()
    new_hash_lib.update(concatenated)
    new_digest = new_hash_lib.digest()
    return new_digest


def calculate_root_hash_from_internal_hashes(internal_hashes, leaf_hash):
    """
    Combine the internal hashes and the leaf hash until only one root hash remains.

    :type internal_hashes: map
    :param internal_hashes: An iterable over a list of hash values.

    :type leaf_hash: bytes
    :param leaf_hash: The revision hash to pair with the first hash in the Proof hashes list.

    :rtype: bytes
    :return: The root hash constructed by combining internal hashes.
    """
    root_hash = reduce(join_hash_pairwise, internal_hashes, leaf_hash)
    return root_hash


def build_candidate_digest(proof, leaf_hash):
    """
    Build the candidate digest representing the entire ledger from the Proof hashes.

    :type proof: dict
    :param proof: The Proof object.

    :type leaf_hash: bytes
    :param leaf_hash: The revision hash to pair with the first hash in the Proof hashes list.

    :rtype: bytes
    :return: The calculated root hash.
    """
    parsed_proof = parse_proof(proof)
    root_hash = calculate_root_hash_from_internal_hashes(parsed_proof, leaf_hash)
    return root_hash


def verify_document(document_hash, digest, proof):
    """
    Verify document revision against the provided digest.

    :type document_hash: bytes
    :param document_hash: The SHA-256 value representing the document revision to be verified.

    :type digest: bytes
    :param digest: The SHA-256 hash value representing the ledger digest.

    :type proof: dict
    :param proof: The Proof object retrieved from :func:`pyqldbsamples.get_revision.get_revision`.

    :rtype: bool
    :return: If the document revision verify against the ledger digest.
    """
    candidate_digest = build_candidate_digest(proof, document_hash)
    return digest == candidate_digest


def to_base_64(input):
    """
    Encode input in base64.

    :type input: bytes
    :param input: Input to be encoded.

    :rtype: string
    :return: Return input that has been encoded in base64.
    """
    encoded_value = b64encode(input)
    return str(encoded_value, "UTF-8")


def value_holder_to_string(value_holder):
    """
    Returns the string representation of a given `value_holder`.

    :type value_holder: dict
    :param value_holder: The `value_holder` to convert to string.

    :rtype: str
    :return: The string representation of the supplied `value_holder`.
    """
    ret_val = dumps(loads(value_holder), binary=False, indent="  ", omit_version_marker=True)
    val = "{{ IonText: {}}}".format(ret_val)
    return val


def block_response_to_string(block_response):
    """
    Returns the string representation of a given `block_response`.

    :type block_response: dict
    :param block_response: The `block_response` to convert to string.

    :rtype: str
    :return: The string representation of the supplied `block_response`.
    """
    string = ""
    if block_response.get("Block", {}).get("IonText") is not None:
        string += "Block: " + value_holder_to_string(block_response["Block"]["IonText"]) + ", "

    if block_response.get("Proof", {}).get("IonText") is not None:
        string += "Proof: " + value_holder_to_string(block_response["Proof"]["IonText"])

    return "{" + string + "}"


def digest_response_to_string(digest_response):
    """
    Returns the string representation of a given `digest_response`.

    :type digest_response: dict
    :param digest_response: The `digest_response` to convert to string.

    :rtype: str
    :return: The string representation of the supplied `digest_response`.
    """
    string = ""
    if digest_response.get("Digest") is not None:
        string += "Digest: " + str(digest_response["Digest"]) + ", "

    if digest_response.get("DigestTipAddress", {}).get("IonText") is not None:
        string += "DigestTipAddress: " + value_holder_to_string(
            digest_response["DigestTipAddress"]["IonText"]
        )

    return "{" + string + "}"


# Deviation from AWS documentation: added qldb_client argument
def get_digest_result(qldb_client, name):
    """
    Get the digest of a ledger's journal.

    :param qldb_client:
    :type name: str
    :param name: Name of the ledger to operate on.

    :rtype: dict
    :return: The digest in a 256-bit hash value and a block address.
    """
    logger.info("Let's get the current digest of the ledger named {}".format(name))
    result = qldb_client.get_digest(Name=name)
    logger.info("Success. LedgerDigest: {}.".format(digest_response_to_string(result)))
    return result


# Deviation from AWS documentation: added qldb_client argument
def get_revision(qldb_client, ledger_name, document_id, block_address, digest_tip_address):
    """
    Get the revision data object for a specified document ID and block address.
    Also returns a proof of the specified revision for verification.

    :type ledger_name: str
    :param ledger_name: Name of the ledger containing the document to query.

    :type document_id: str
    :param document_id: Unique ID for the document to be verified, contained in the committed view of the document.

    :type block_address: dict
    :param block_address: The location of the block to request.

    :type digest_tip_address: dict
    :param digest_tip_address: The latest block location covered by the digest.

    :rtype: dict
    :return: The response of the request.
    """
    result = qldb_client.get_revision(
        Name=ledger_name,
        BlockAddress=block_address,
        DocumentId=document_id,
        DigestTipAddress=digest_tip_address,
    )
    return result


def lookup_registration_for_vin(driver, vin):
    """
    Query revision history for a particular vehicle for verification.

    :type driver: :py:class:`pyqldb.driver.qldb_driver.QldbDriver`
    :param driver: An instance of the QldbDriver class.

    :type vin: str
    :param vin: VIN to query the revision history of a specific registration with.

    :rtype: :py:class:`pyqldb.cursor.buffered_cursor.BufferedCursor`
    :return: Cursor on the result set of the statement query.
    """
    logger.info("Querying the 'VehicleRegistration' table for VIN: {}...".format(vin))
    query = "SELECT * FROM _ql_committed_VehicleRegistration WHERE data.VIN = ?"
    return driver.execute_lambda(
        lambda txn: txn.execute_statement(query, convert_object_to_ion(vin))
    )


# Deviation from AWS documentation: added qldb_client argument
def verify_registration(qldb_client, driver, ledger_name, vin):
    """
    Verify each version of the registration for the given VIN.

    :type driver: :py:class:`pyqldb.driver.qldb_driver.QldbDriver`
    :param driver: An instance of the QldbDriver class.

    :type ledger_name: str
    :param ledger_name: The ledger to get digest from.

    :type vin: str
    :param vin: VIN to query the revision history of a specific registration with.

    :raises AssertionError: When verification failed.
    """
    logger.info(
        "Let's verify the registration with VIN = {}, in ledger = {}.".format(vin, ledger_name)
    )
    digest = get_digest_result(qldb_client, ledger_name)
    digest_bytes = digest.get("Digest")
    digest_tip_address = digest.get("DigestTipAddress")

    logger.info(
        "Got a ledger digest: digest tip address = {}, digest = {}.".format(
            value_holder_to_string(digest_tip_address.get("IonText")),
            to_base_64(digest_bytes),
        )
    )

    logger.info(
        "Querying the registration with VIN = {} to verify each version of the registration...".format(
            vin
        )
    )
    cursor = lookup_registration_for_vin(driver, vin)
    logger.info("Getting a proof for the document.")

    for row in cursor:
        block_address = row.get("blockAddress")
        document_id = row.get("metadata").get("id")

        result = get_revision(
            qldb_client,
            ledger_name,
            document_id,
            block_address_to_dictionary(block_address),
            digest_tip_address,
        )
        revision = result.get("Revision").get("IonText")
        document_hash = loads(revision).get("hash")

        proof = result.get("Proof")
        logger.info("Got back a proof: {}.".format(proof))

        verified = verify_document(document_hash, digest_bytes, proof)
        if not verified:
            raise AssertionError("Document revision is not verified.")
        else:
            logger.info("Success! The document is verified.")

        altered_document_hash = flip_random_bit(document_hash)
        logger.info(
            "Flipping one bit in the document's hash and assert that the document is NOT verified. "
            "The altered document hash is: {}.".format(to_base_64(altered_document_hash))
        )
        verified = verify_document(altered_document_hash, digest_bytes, proof)
        if verified:
            raise AssertionError(
                "Expected altered document hash to not be verified against digest."
            )
        else:
            logger.info(
                "Success! As expected flipping a bit in the document hash causes verification to fail."
            )

        logger.info(
            "Finished verifying the registration with VIN = {} in ledger = {}.".format(
                vin, ledger_name
            )
        )
