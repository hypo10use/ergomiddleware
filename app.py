from flask import Flask, render_template, request
import requests, json
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/ergoscript', methods = ['POST'])
@cross_origin()
def compile_ergoscript():
    headers = {'content-type': 'application/json'}
    json_data = request.json
    script = json_data['script']
    r=requests.post("http://116.203.30.147:9053/script/p2sAddress", data=json.dumps({'source': script}), headers=headers)
    return r.text

@app.route('/create_round', methods = ['POST'])
def create_round():
    headers = {'content-type': 'application/json'}
    json_data = request.json
    script = json_data['script']
    script = '''{
         |  val totalSoldTicket = SELF.R4[Long].get
         |  val totalSoldTicketBI: BigInt = totalSoldTicket.toBigInt
         |  val totalRaised = totalSoldTicket * ticketPrice
         |  val projectCoef = SELF.R6[Long].get
         |  val winnerCoef = 100L - projectCoef
         |  sigmaProp(
         |    if (HEIGHT < deadlineHeight) {
         |      allOf(Coll(
         |            // validate Script
         |            OUTPUTS(0).propositionBytes == SELF.propositionBytes,
         |            blake2b256(OUTPUTS(1).propositionBytes) == ticketScriptHash,
         |            OUTPUTS(1).R6[Coll[Byte]].get == blake2b256(SELF.propositionBytes),
         |            // minERG
         |            INPUTS(1).value >= ticketPrice + 2 * minFee,
         |            // validate Register
         |            OUTPUTS(0).R4[Long].get == totalSoldTicket + (INPUTS(1).value - 2 * minFee) / ticketPrice,
         |            OUTPUTS(1).R4[Long].get == totalSoldTicket,
         |            OUTPUTS(1).R5[Long].get == (INPUTS(1).value - 2 * minFee) / ticketPrice,
         |            // validate Token
         |            OUTPUTS(0).tokens(0)._1 == SELF.tokens(0)._1,
         |            OUTPUTS(0).tokens(0)._2 == SELF.tokens(0)._2 - (INPUTS(1).value - 2 * minFee) / ticketPrice,
         |            OUTPUTS(0).tokens(1)._1 == SELF.tokens(1)._1, // Raffle Service Token
         |            OUTPUTS(1).tokens(0)._1 == SELF.tokens(0)._1,
         |            OUTPUTS(1).tokens(0)._2 == (INPUTS(1).value - 2 * minFee) / ticketPrice,
         |            // ERG Protect
         |            OUTPUTS(0).value == SELF.value + INPUTS(1).value - 2 * minFee,
         |            OUTPUTS(1).value == minFee,
         |            // same Coef
         |            OUTPUTS(0).R6[Long].get == projectCoef
         |            ))
         |    }
         |    else {
         |      if (totalRaised >= minToRaise) {
         |        allOf(Coll(
         |              // Validate Size
         |              INPUTS.size == 1 && OUTPUTS.size == 5,
         |              // Pay Back Raffle Service Token
         |              OUTPUTS(0).tokens(0)._1 == SELF.tokens(1)._1,
         |              OUTPUTS(0).tokens(0)._2 == 1,
         |              OUTPUTS(0).propositionBytes == servicePubKey.propBytes,
         |              // Project Box
         |              OUTPUTS(1).value >= totalRaised * projectCoef / 100,
         |              OUTPUTS(1).propositionBytes == servicePubKey.propBytes,
         |              // Winner Box
         |              OUTPUTS(2).value  >= totalRaised * winnerCoef / 100,
         |              blake2b256(OUTPUTS(3).propositionBytes) == winnerScriptHash,
         |              OUTPUTS(2).R4[Long].get == ((byteArrayToBigInt(CONTEXT.dataInputs(0).id.slice(0, 15)).toBigInt + totalSoldTicketBI) % totalSoldTicketBI).toBigInt,
         |              OUTPUTS(2).tokens(0)._1 == SELF.tokens(0)._1,
         |              OUTPUTS(2).tokens(0)._2 == SELF.tokens(0)._2
         |         ))
         |      }
         |      else {
         |      if (totalRaised < minToRaise) {
         |        if(totalSoldTicket > 0){
         |          allOf(Coll(
         |                // validate Script
         |                OUTPUTS(0).propositionBytes == SELF.propositionBytes,
         |                // validate Token & ERG
         |                OUTPUTS(0).tokens(0)._1 == SELF.tokens(0)._1,
         |                OUTPUTS(0).value >= SELF.value - (OUTPUTS(0).tokens(0)._2 - SELF.tokens(0)._2) * ticketPrice,
         |                OUTPUTS(0).tokens(0)._2 > SELF.tokens(0)._2,
         |                OUTPUTS(0).R4[Long].get == SELF.R4[Long].get - (OUTPUTS(0).tokens(0)._2 - SELF.tokens(0)._2)
         |          ))
         |        }
         |        else
         |        {
         |          allOf(Coll(
         |                // Pay Back Raffle Service Token
         |                OUTPUTS(0).tokens(0)._1 == SELF.tokens(1)._1,
         |                OUTPUTS(0).tokens(0)._2 == 1,
         |                OUTPUTS(0).propositionBytes == servicePubKey.propBytes
         |          ))
         |        }
         |      }
         |      else {
         |        false
         |      }
         |    }
         |  })
         |}'''
    r=requests.post("http://116.203.30.147:9053/script/p2sAddress", data=json.dumps({'source': script}), headers=headers)
    return r.text


def ticket():
    headers = {'content-type': 'application/json'}
    json_data = request.json
    script = json_data['script']
    script = '''{
         |  val refundPhaseSpend = HEIGHT > deadlineHeight &&
         |                         blake2b256(INPUTS(0).propositionBytes) == SELF.R6[Coll[Byte]].get &&
         |                         INPUTS(0).tokens(0)._1 == SELF.tokens(0)._1
         |
         |  val winnerPhaseSpend = HEIGHT > deadlineHeight &&
         |                         blake2b256(INPUTS(0).propositionBytes) == winnerScriptHash &&
         |                         INPUTS(0).tokens(0)._1 == SELF.tokens(0)._1
         |
         |  val receiverCheck = OUTPUTS(1).propositionBytes  == SELF.R7[Coll[Byte]].get &&
         |                      OUTPUTS(1).value == SELF.tokens(0)._2 * ticketPrice &&
         |                      INPUTS.size == 2
         |
         |  val receiverCheckWinner = OUTPUTS(0).propositionBytes == SELF.R7[Coll[Byte]].get &&
         |                            OUTPUTS(0).value == INPUTS(0).value
         |
         |  sigmaProp((receiverCheck && refundPhaseSpend) || (receiverCheckWinner && winnerPhaseSpend))
         |}'''
    r=requests.post("http://116.203.30.147:9053/script/p2sAddress", data=json.dumps({'source': script}), headers=headers)
    return r.text


def check_winnings():
    headers = {'content-type': 'application/json'}
    json_data = request.json
    script = json_data['script']
    script = '''{
         |  sigmaProp(
         |    allOf(Coll(
         |          // Valid Ticket
         |          INPUTS(1).tokens(0)._1 == SELF.tokens(0)._1,
         |          INPUTS(1).R4[Long].get <= SELF.R4[Long].get,
         |          INPUTS(1).R4[Long].get + INPUTS(1).R5[Long].get > SELF.R4[Long].get
         |    ))
         |  )
         |}'''
    r=requests.post("http://116.203.30.147:9053/script/p2sAddress", data=json.dumps({'source': script}), headers=headers)
    return r.text


if __name__ == '__main__': app.run(debug=True)