import React, { Component } from 'react'
import { Pagination } from 'react-bootstrap';

class Paginator extends Component {
    paginationItems;
    handlePageChange;
    activePage;
    constructor(props) {
        super(props);

        this.paginationItems = [];
        this.handlePageChange = props.handlePageChange;
        this.activePage = props.activePage;
        this.pages = props.pages;
    };

    initPageinationItems = (pages, activePage) => {
        let items = [];
        for (let number = 1; number <= pages; number++) {
            items.push(
                <Pagination.Item key={number}
                    active={number === activePage}
                    onClick={() => this.handlePageChange(number)}>
                    {number}
                </Pagination.Item>,
            );
        }
        this.paginationItems = items
    }

    render() {
        this.initPageinationItems(this.pages, this.activePage)
        return (
            < Pagination aria-label="Page navigation">
                <Pagination.First
                    onClick={() => this.handlePageChange(1)} />
                <Pagination.Prev
                    onClick={() => this.handlePageChange(
                        this.activePage - 1)} />
                {this.paginationItems}
                <Pagination.Next
                    onClick={() => this.handlePageChange(
                        this.activePage + 1)} />
                <Pagination.Last
                    onClick={() => this.handlePageChange(
                        this.pages)} />
            </ Pagination>
        )
    }
}

export default Paginator;