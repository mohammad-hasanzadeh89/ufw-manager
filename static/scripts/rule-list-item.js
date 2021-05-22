import React, { Component } from 'react'
import { Button } from 'react-bootstrap';
import '../css/app.css';
class RuleListItem extends Component {
    constructor(props) {
        super(props);

        this.state = {
            rule: props.rule,
            deleteConfirmOpener: props.deleteConfirmOpener,
            editRule: props.editRule
        }
    }

    cleanRuleFromNull = (obj) => {
        let temp = {}

        let keys = Object.keys(obj);
        for (let i = 0; i < keys.length; i++) {
            let key = keys[i]
            let val = obj[key]
            if (val === null)
                val = "null"
            temp[key] = val
        }
        return temp
    }

    render() {
        const rule = this.cleanRuleFromNull(this.state.rule)
        return (
            <tr>
                <td>{rule.id.toString()}</td>
                <td>{rule.user_id.toString()}</td>
                <td>{rule.rule_command}</td>
                <td>{rule.rule_action}</td>
                <td>{rule.in_out}</td>
                <td>{rule.from_IP.toString()}</td>
                <td>{rule.from_port.toString()}</td>
                <td>{rule.from_service_name}</td>
                <td>{rule.to_IP.toString()}</td>
                <td>{rule.to_port.toString()}</td>
                <td>{rule.to_service_name}</td>
                <td>{rule.protocol.toString()}</td>
                <td>{rule.comment}</td>
                <td>{rule.add_date}</td>
                <td>
                    <Button
                        style={{ marginRight: '1rem' }}

                        variant="warning"
                        onClick={
                            () => { this.state.editRule(this.state.rule) }}>
                        Edit
                    </Button>
                    <Button
                        variant="danger"
                        onClick={
                            () => { this.state.deleteConfirmOpener(this.state.rule) }}>
                        Delete
                    </Button>
                </td>

            </tr>


        );
    }

};

export default RuleListItem;