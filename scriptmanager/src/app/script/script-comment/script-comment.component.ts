import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import * as $ from 'jquery';
import { CommentsService } from 'src/app/_service/comments.service';
import { AlertService } from 'src/app/services/alert.service';

@Component({
  selector: 'app-script-comment',
  templateUrl: './script-comment.component.html',
  styleUrls: ['./script-comment.component.sass']
})
export class ScriptCommentComponent implements OnInit {
  @Input() newComment: string = "";
  @Input() comments: any;
  @Input() published: boolean = false;
  @Output() commentEmitter = new EventEmitter<string>();
  comment_value = "";
  isEditable = false;

  constructor(
    private commentService: CommentsService,
    private alertService: AlertService
  ) { }

  public addComment() {
    if (this.newComment.trim() != "") {
      this.commentEmitter.emit(this.newComment);
      this.newComment = "";
      this.comment_value = "";
    }
  }


  commentKey(event) { this.newComment = event.target.value; }

  saveComment(index) {
    this.commentService.modifyComment(
      this.comments[index]['id'], 
      {'comment': this.comments[index].comment}
    ).subscribe(
        (res) => {
          this.comments[index] = res['data'];
          this.alertService.success(res['message']);
        },
        console.error
      );
  };

  deleteComment(index) {
    this.commentService.deleteComment(this.comments[index]['id'])
      .subscribe(
        (res) => this.comments.splice(index, 1),
        (err) => this.alertService.error(err)
      );
  }

  doneComment(index) {
    this.commentService.changeCommentDoneStatus(this.comments[index]['id'], !this.comments[index]['done'])
      .subscribe(
        (res) => {
          this.comments[index] = res['data'];
        },
        console.error
      );
  }

  resolveComment(index) {
    this.commentService.changeCommentResolvedStatus(this.comments[index]['id'], !this.comments[index]['resolved'])
      .subscribe(
        (res) => {
          this.comments[index] = res['data'];
        },
        console.error
      );
  }

  ngOnInit() {
    var element = document.getElementById("fixedComments");
    element.scrollTop = element.scrollHeight;
  }

}