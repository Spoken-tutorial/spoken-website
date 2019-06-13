import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-script-comment',
  templateUrl: './script-comment.component.html',
  styleUrls: ['./script-comment.component.sass']
})
export class ScriptCommentComponent implements OnInit {
  public comments: any = [];

  constructor() { }

  public viewComment() {
    // this.createscriptService.getComment(
    //   this.id
    // ).subscribe(
    //   (res) => {
    //       for(let i =0;i<res['length'];i++){
    //         this.slides.push(res[i]);
    //       }
    //   },
    //   console.error
    // );

    return [
      {
        "slideId": 1,
        "user": "Reviewer 1", 
        "comment": "This comment is from reviewer 1"
      },
      {
        "slideId": 2,
        "user": "Reviewer 2", 
        "comment": "This comment is from reviewer 2"
      },
      {
        "slideId": 1,
        "user": "Reviewer 3", 
        "comment": "This comment is from reviewer 3"
      },
      {
        "slideId": 4,
        "user": "Reviewer 4", 
        "comment": "This comment is from reviewer 4"
      }
    ]
  }

  ngOnInit() {
    // this.route.params.subscribe(params => {
    //   this.id = +params['id'];
    // });
    this.comments = this.viewComment();
    console.log(this.comments)
  }

}